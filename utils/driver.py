from pathlib import Path

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver


def _start_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    options.add_argument(f"user-data-dir={Path().absolute() / 'selenium'}")
    options.add_argument("--window-size=1920,1080")
    if headless:
        options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


class WebDriver:
    __instance__: webdriver.Chrome | None = None

    def __init__(self, headless: bool = False) -> None:
        if WebDriver.__instance__ is not None:
            raise RuntimeError("Cannot init class twice, as it is as singelton")
        WebDriver.__instance__ = _start_driver(headless=headless)

    @classmethod
    def get_instance(cls, headless: bool = False) -> webdriver.Chrome:
        if cls.__instance__ is None:
            WebDriver(headless=headless)
        return cls.__instance__
