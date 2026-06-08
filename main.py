import argparse
import os

from dotenv import load_dotenv

from utils.driver import WebDriver
from utils.processer import markdownify
from utils.retriever import download_profile, login_to_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Export LinkedIn profile to Markdown")
    parser.add_argument("--template", default="peppermint.md", help="Jinja2 template to use")
    parser.add_argument("--cached", action="store_true", help="Skip scraping, use cached HTML")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    parser.add_argument("--omit", nargs="*", default=[], help="Sections to exclude from scraping")
    parser.add_argument(
        "--json", metavar="PATH", nargs="?", const="data/extracted.json", help="Export extracted data as JSON"
    )
    args = parser.parse_args()

    if not args.cached:
        load_dotenv()
        profile_url = login_to_profile(
            os.getenv("MAIL"),
            os.getenv("PASSWORD"),
            headless=args.headless,
        )
        download_profile(profile_url, args.omit, headless=args.headless)
        WebDriver.get_instance().quit()

    markdownify(template_name=args.template, json_path=args.json)


if __name__ == "__main__":
    main()
