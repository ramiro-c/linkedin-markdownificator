import json
import os
from typing import Any

from bs4 import BeautifulSoup as bs
from jinja2 import Environment, FileSystemLoader
from parsel import Selector


def repeated_string(s: str) -> str:
    half = len(s) // 2
    return s[:half] if s[half:] == s[:half] else s


source_override: dict[str, str] = {"volunteering": "main"}


def _enrich_experience(extracted: dict[str, Any]) -> dict[str, Any]:
    if "experience" not in extracted:
        return extracted
    enriched_basic: list[list[str]] = []
    enriched_desc: list[Any] = []
    current_company: str | None = None
    current_location: str | None = None
    desc_idx = 0
    skills_list = extracted.get("experience", {}).get("skills", [])
    for item in extracted["experience"]["basic"]:
        if len(item) == 3:
            current_company = item[0]
            current_location = item[2]
        elif len(item) == 2:
            company = current_company or item[0]
            location = current_location or ""
            enriched_basic.append([item[0], company, item[1], location])
            if desc_idx < len(extracted["experience"]["description"]):
                desc = list(extracted["experience"]["description"][desc_idx])
                if desc_idx < len(skills_list) and skills_list[desc_idx]:
                    desc.append(skills_list[desc_idx][0])
                enriched_desc.append(desc)
                desc_idx += 1
        elif len(item) == 4:
            company = item[1].split(" · ")[0] if " · " in item[1] else item[1]
            enriched_basic.append([item[0], company, item[2], item[3]])
            if desc_idx < len(extracted["experience"]["description"]):
                desc = list(extracted["experience"]["description"][desc_idx])
                if desc_idx < len(skills_list) and skills_list[desc_idx]:
                    desc.append(skills_list[desc_idx][0])
                enriched_desc.append(desc)
                desc_idx += 1
    extracted["experience"]["basic"] = enriched_basic
    extracted["experience"]["description"] = enriched_desc
    extracted["experience"].pop("skills", None)
    return extracted


def markdownify(template_name: str = "peppermint.md", json_path: str | None = None) -> None:
    with open("selectors.json", encoding="utf-8") as f:
        to_extract = json.load(f)

    extracted: dict[str, Any] = {}
    for key in list(to_extract.keys()):
        extracted[key] = {}
        source = source_override.get(key, key)
        try:
            with open(f"data/{source}.html", encoding="utf-8") as html_content:
                selector = Selector(html_content.read())
        except FileNotFoundError:
            print(f"Warning: data/{source}.html not found, skipping {key}")
            for item in to_extract[key].items():
                if isinstance(item[1], str):
                    extracted[key][item[0]] = []
            continue

        for item in to_extract[key].items():
            if not isinstance(item[1], str):
                continue
            try:
                res = selector.css(item[1]).getall()
            except Exception:
                continue
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

    extracted = _enrich_experience(extracted)

    for entry in extracted.get("projects", {}).get("basic", []):
        if len(entry) < 2:
            entry.append("")

    if json_path:
        os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(extracted, f, indent=2)

    template_loader = FileSystemLoader(searchpath="./templates")
    template_env = Environment(loader=template_loader)
    template = template_env.get_template(template_name)

    output_text = template.render(extracted, zip=zip, len=len)

    with open("output.md", "w", encoding="utf-8") as out:
        out.write(output_text)
