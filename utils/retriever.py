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

        wait = WebDriverWait(driver, 15)
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/in/')]")))
        profile_link.click()
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

        return driver.current_url
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
            WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
        else:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

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
