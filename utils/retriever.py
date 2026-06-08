import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver import WebDriver


def login_to_profile(mail, password):
    driver = WebDriver.get_instance()
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


retrieval = (
    "main",
    "featured",
    "experience",
    "education",
    "certifications",
    "projects",
    "honors",
    "languages",
)


def download_profile(profile_url, omit=None):
    if omit is None:
        omit = []
    driver = WebDriver.get_instance()

    to_retrieve = [i for i in list(retrieval) if i not in omit]
    for element in to_retrieve:
        os.makedirs(os.path.dirname(f"data/{element}.html"), exist_ok=True)
        print(f"scraping: {element}")
        if element != "main":
            driver.get(profile_url + f"details/{element}/")
            WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        with open(f"data/{element}.html", "w", encoding="utf-8") as element_file:
            element_file.write(driver.page_source)
            element_file.write("\n")
        print(f"  saved data/{element}.html ({len(driver.page_source)} bytes)")
