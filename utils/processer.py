
from bs4 import BeautifulSoup as bs
from jinja2 import Environment, FileSystemLoader
from parsel import Selector


def repeated_string(s):
    half = len(s) // 2
    return s[:half] if s[half:] == s[:half] else s


to_extract = {
    "main": {
        "name": "h1",
        "description": "div > div.scaffold-layout.scaffold-layout--breakpoint-xl.scaffold-layout--main-aside.scaffold-layout--reflow.pv-profile.pvs-loader-wrapper__shimmer--animate > div > div > main > section > div.ph5 > div.mt2.relative > div:nth-child(1) > div.text-body-medium.break-words",
        "main_skills": "div > div.scaffold-layout.scaffold-layout--breakpoint-xl.scaffold-layout--main-aside.scaffold-layout--reflow.pv-profile.pvs-loader-wrapper__shimmer--animate > div > div > main > section:nth-child(4) > div:nth-child(4) > div > ul > li > div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > div > div:nth-child(2)",
    },
    "featured": {"title": '.pv-profile-component-builder__card [class*="inline-show-more-text"]'},
    "experience": {
        "basic": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between",
        "description": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > ul > li:nth-child(1) > div > ul > li > div",
    },
    "education": {
        "basic": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > a",
        "description": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > a",
    },
    "certifications": {
        "basic": "section.artdeco-card.pb3 .display-flex.flex-column.full-width",
        "dates": "section.artdeco-card.pb3 span.pvs-entity__caption-wrapper",
        "description": "section.artdeco-card.pb3 .pvs-entity__sub-components",
    },
    "projects": {
        "basic": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > div > div > div > div",
        "description": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > ul > li:nth-child(1)",
        "skills": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > ul > li:nth-child(2)",
    },
    "volunteering": {
        "basic": "#volunteering_experience ~ div ul li.artdeco-list__item div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between",
        "description": "#volunteering_experience ~ div ul li.artdeco-list__item div.pvs-entity__sub-components",
    },
    "languages": {"languages": "section.artdeco-card.pb3 .display-flex.flex-column.full-width"},
}

source_override = {"volunteering": "main"}


def markdownify():
    extracted = {}
    for key in list(to_extract.keys()):
        extracted[key] = {}
        source = source_override.get(key, key)
        with open(f"data/{source}.html", encoding="utf-8") as html_content:
            selector = Selector(html_content.read())

        for item in to_extract[key].items():
            if not isinstance(item[1], str):
                continue
            res = selector.css(item[1]).getall()
            for index in range(len(res)):
                soup = bs(res[index], features="lxml")
                for hidden in soup.select(".visually-hidden"):
                    hidden.decompose()
                for br in soup.find_all("br"):
                    br.replace_with("\n")
                text = soup.get_text().strip()
                res[index] = text.split("\n")
                res[index] = [repeated_string(item) for item in res[index] if item.strip()]
            extracted[key] |= {item[0]: res}

    if "experience" in extracted:
        enriched_basic = []
        enriched_desc = []
        current_company = None
        current_location = None
        desc_idx = 0
        for item in extracted["experience"]["basic"]:
            if len(item) == 3:
                current_company = item[0]
                current_location = item[2]
            elif len(item) == 2:
                company = current_company or item[0]
                location = current_location or ""
                enriched_basic.append([item[0], company, item[1], location])
                if desc_idx < len(extracted["experience"]["description"]):
                    enriched_desc.append(extracted["experience"]["description"][desc_idx])
                    desc_idx += 1
            elif len(item) == 4:
                company = item[1].split(" · ")[0] if " · " in item[1] else item[1]
                enriched_basic.append([item[0], company, item[2], item[3]])
                if desc_idx < len(extracted["experience"]["description"]):
                    enriched_desc.append(extracted["experience"]["description"][desc_idx])
                    desc_idx += 1
        extracted["experience"]["basic"] = enriched_basic
        extracted["experience"]["description"] = enriched_desc

    template_loader = FileSystemLoader(searchpath="./templates")
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("peppermint.md")

    output_text = template.render(extracted, zip=zip, len=len)

    with open("output.md", "w", encoding="utf-8") as out:
        out.write(output_text)
