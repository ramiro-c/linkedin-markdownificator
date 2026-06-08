import os

from dotenv import load_dotenv

from utils.driver import WebDriver
from utils.processer import markdownify
from utils.retriever import download_profile, login_to_profile

load_dotenv()

profile_url = login_to_profile(os.getenv("MAIL"), os.getenv("PASSWORD"))

download_profile(
    profile_url,
    [
        "honors",
    ],
)

WebDriver.get_instance().quit()

markdownify()
