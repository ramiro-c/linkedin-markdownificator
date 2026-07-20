import contextlib
import functools
import os
import time
from collections.abc import Callable
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver import WebDriver


def retry(max_attempts: int = 3, base_delay: int | float = 1) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts:
                        delay = base_delay * (2 ** (attempt - 1))
                        print(f"  retry {attempt}/{max_attempts - 1} for {args[0] if args else ''} after {delay}s: {e}")
                        time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator


def login_to_profile(mail: str, password: str, headless: bool = False) -> str:
    try:
        driver = WebDriver.get_instance(headless=headless)
        driver.get("https://linkedin.com/login")
        driver.implicitly_wait(15)

        if "feed" not in driver.title.lower():
            print("login required")
            wait = WebDriverWait(driver, 30)
            username = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username.send_keys(mail)
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(password, Keys.ENTER)
            WebDriverWait(driver, 60).until(lambda d: "feed" in d.title.lower())

        # Navigate to the profile by URL rather than clicking: the first
        # //a[@href*='/in/'] match is the global-nav "Me" item, which opens a
        # JS dropdown instead of navigating, leaving the driver on /feed/.
        wait = WebDriverWait(driver, 15)
        profile_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/in/')]")))
        profile_href = profile_link.get_attribute("href")
        driver.get(profile_href)
        WebDriverWait(driver, 15).until(lambda d: "/in/" in d.current_url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Ensure a trailing slash so `profile_url + "details/<slug>/"` builds valid URLs.
        return driver.current_url if driver.current_url.endswith("/") else driver.current_url + "/"
    except Exception as e:
        print(f"login failed: {e}")
        raise


retrieval: tuple[str, ...] = (
    "main",
    "featured",
    "experience",
    "education",
    "certifications",
    "projects",
    "honors",
    "languages",
)


def download_profile(profile_url: str, omit: list[str] | None = None, headless: bool = False) -> None:
    if omit is None:
        omit = []
    driver = WebDriver.get_instance(headless=headless)

    @retry(max_attempts=4, base_delay=1)
    def scrape_section(element_slug: str) -> None:
        if element_slug != "main":
            driver.get(profile_url + f"details/{element_slug}/")
            WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
            # Gradually scroll to trigger LinkedIn's LazyColumn rendering.
            # A single full-page scroll often misses lazy items; step-scroll is more reliable.
            driver.execute_script(
                "var h = document.body.scrollHeight;"
                "var step = Math.ceil(h / 4);"
                "for (var i = step; i <= h; i += step) { window.scrollTo(0, i); }"
            )
            # Wait for at least one entity-collection-item to have visible children,
            # giving lazy components up to 10 s to hydrate. The section may genuinely
            # be empty (e.g. honors), so suppress the timeout and carry on.
            with contextlib.suppress(Exception):
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script(
                        "return document.querySelectorAll('[componentkey*=\"entity-collection-item\"]').length > 0;"
                    )
                )
            WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
        else:
            driver.get(profile_url)
            WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
            # Gradually scroll to trigger LinkedIn's LazyColumn rendering, same as the
            # detail sub-pages: the About/pinned-skills card below the activity section
            # is lazy-hydrated and never renders into page_source without this.
            driver.execute_script(
                "var h = document.body.scrollHeight;"
                "var step = Math.ceil(h / 4);"
                "for (var i = step; i <= h; i += step) { window.scrollTo(0, i); }"
            )
            # Wait for the About/Highlights SDUI card (componentkey containing the
            # case-sensitive substring "About") to have actual text content, not just
            # an empty placeholder div. Measured live: querySelectorAll alone returns
            # non-empty elements instantly even before hydration, so the check must
            # look at innerText, not just presence. The match must stay case-sensitive
            # here to agree with the extractor: utils/processer.py's
            # _extract_about_and_skills() reads `contains(@componentkey, "About")`,
            # which deliberately excludes the lowercase "<slug>_about_edit" edit-button
            # componentkey. A case-insensitive wait would match that edit button and
            # could resolve as soon as *it* hydrates, before the real About/skills card
            # does — saving unhydrated HTML with no error (this whole block is wrapped
            # in contextlib.suppress). The wait and the extraction must agree on what
            # counts as "the real card", not just "anything with about in the name".
            # The section may genuinely be empty (no About/pinned skills), so suppress
            # the timeout and carry on.
            with contextlib.suppress(Exception):
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script(
                        "var els = document.querySelectorAll('[componentkey*=\"About\"]');"
                        "var total = 0;"
                        "els.forEach(function(e) { total += (e.innerText || '').length; });"
                        "return total > 0;"
                    )
                )
            WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")

        with open(f"data/{element_slug}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            f.write("\n")
        print(f"  saved data/{element_slug}.html ({len(driver.page_source)} bytes)")

    try:
        to_retrieve = [i for i in list(retrieval) if i not in omit]
        for element in to_retrieve:
            os.makedirs(os.path.dirname(f"data/{element}.html"), exist_ok=True)
            print(f"scraping: {element}")
            scrape_section(element)
    except Exception as e:
        print(f"download failed: {e}")
        raise
