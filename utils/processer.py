import json
import os
import re
import warnings
from typing import Any

from bs4 import BeautifulSoup as bs
from bs4 import MarkupResemblesLocatorWarning
from jinja2 import Environment, FileSystemLoader
from parsel import Selector

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def repeated_string(s: str) -> str:
    half = len(s) // 2
    return s[:half] if s[half:] == s[:half] else s


source_override: dict[str, str] = {"volunteering": "main", "about": "main"}


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


def _is_new_layout(html: str) -> bool:
    """Detect LinkedIn's post-2025 React layout (componentkey attributes).

    When componentkey is present, the page uses the new React-based layout and we
    should prefer the _extract_new_layout parser. The old artdeco-style selectors
    are unreliable on pages that have both markers (LinkedIn sometimes renders
    sections with a mix of old and new classes).
    """
    return 'componentkey="' in html


def _clean_texts(el_html: str, exclude_keywords: tuple[str, ...] = ("anuncio", "publicidad")) -> list[str]:
    """Extract non-empty, non-ad p-tag texts from an HTML fragment."""
    soup = bs(el_html, features="lxml")
    for hidden in soup.select(".visually-hidden"):
        hidden.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    ps = soup.find_all("p")
    results = []
    for p in ps:
        text = p.get_text(separator="\n").strip()
        lines = [repeated_string(ln) for ln in text.split("\n") if ln.strip()]
        if not lines:
            continue
        combined = " ".join(lines)
        if any(kw in combined.lower() for kw in exclude_keywords):
            continue
        results.append(combined)
    return results


def _entity_texts(entity_html: str) -> list[str]:
    return _clean_texts(entity_html)


def _normalize_skills(line: str) -> str:
    """Ensure a skills line carries the 'Aptitudes: ' prefix (single-role entries omit it)."""
    if line and "aptitud" in line.lower() and not line.lower().startswith("aptitudes:"):
        return f"Aptitudes: {line}"
    return line


_SKILLS_LABELS = ("principales aptitudes", "top skills")


def _join_about_paragraphs(text: str) -> str:
    """Group <br>-separated lines back into paragraphs, deduping each line.

    LinkedIn renders a double <br><br> between logical paragraphs and a
    single <br> for in-paragraph wraps. After the caller replaces every <br>
    with "\\n", blank lines mark paragraph boundaries: lines within a
    paragraph are joined with a space, and paragraphs are joined with a
    blank line so the rendered Markdown keeps real paragraph breaks.
    """
    paragraphs: list[str] = []
    current: list[str] = []
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(repeated_string(line))
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


def _extract_about_and_skills(sel: Selector) -> tuple[str, str]:
    """Extract the About text and the pinned/top skills line from the main page.

    LinkedIn's post-2025 React layout renders "About" and "Principales
    aptitudes"/"Top skills" (pinned skills) inside the *same* SDUI card,
    keyed by a componentkey ending in the case-sensitive substring "About"
    (e.g. "com.linkedin.sdui.profile.card.ref<urn>About"). That casing is
    deliberate: it excludes the lowercase "<slug>_about_edit" edit-button
    componentkey, and the card itself lives entirely outside the page
    <footer> — so the unrelated "Acerca de" / "About LinkedIn" footer link
    (href="https://about.linkedin.com/") can never be picked up by this
    xpath. A `<footer>` decompose below is kept as a defensive no-op in case
    a future markup change nests things differently.

    Within the card, both About and the skills line are plain <p> tags (no
    h2/h3 heading and no pill/list markup for skills, despite earlier
    assumptions) — the skills line itself is already "•"-joined, e.g.
    "React.js • Node.js • Python".
    """
    card_html = sel.xpath('(//*[@componentkey and contains(@componentkey, "About")])[1]').get()
    if not card_html:
        return "", ""

    soup = bs(card_html, features="lxml")
    for footer in soup.find_all("footer"):
        footer.decompose()
    for hidden in soup.select(".visually-hidden"):
        hidden.decompose()
    for btn in soup.find_all("button"):
        btn.decompose()  # "ver más" / "see more" toggle text, not real content
    for br in soup.find_all("br"):
        br.replace_with("\n")

    about_text = ""
    skills_line = ""
    take_next_as_skills = False
    for p in soup.find_all("p"):
        raw_text = p.get_text(separator="\n").strip()
        if not raw_text:
            continue
        if take_next_as_skills:
            lines = [repeated_string(ln.strip()) for ln in raw_text.split("\n") if ln.strip()]
            skills_line = " ".join(lines)
            take_next_as_skills = False
            continue
        if raw_text.strip().lower() in _SKILLS_LABELS:
            take_next_as_skills = True
            continue
        if not about_text:
            about_text = _join_about_paragraphs(raw_text)

    return about_text, skills_line


def _extract_new_layout(section: str, html: str) -> dict[str, Any]:
    """
    Extract profile data from LinkedIn's post-2025 React layout.
    Returns a dict matching the structure expected by the Jinja templates.
    """
    sel = Selector(html)
    entities_html = sel.xpath('//*[@componentkey and contains(@componentkey, "entity-collection-item")]').getall()

    if section == "main":
        # name: first h2 in workspace that is not the toasts title
        name_els = sel.xpath('(//main[@id="workspace"]//h2)[1]').getall()
        name_text = re.sub(r"<[^>]+>", "", name_els[0]).strip() if name_els else ""
        # description/headline: second p in workspace (first is verification badge)
        desc_els = sel.xpath('(//main[@id="workspace"]//p)[2]').getall()
        desc_text = re.sub(r"<[^>]+>", "", desc_els[0]).strip() if desc_els else ""
        desc_text = bs(desc_text, features="lxml").get_text().strip() if desc_text else ""
        _, skills_line = _extract_about_and_skills(sel)
        return {
            "name": [[name_text]] if name_text else [],
            "description": [[desc_text]] if desc_text else [],
            # Pinned/top skills, comma-separated; empty stub so zip still iterates
            # when the profile has none.
            "main_skills": [[skills_line]] if skills_line else [[""]],
        }

    if section == "about":
        about_text, _ = _extract_about_and_skills(sel)
        # Flat [str] shape (max one entry) — unlike name/description/main_skills
        # there's no zip/iteration counterpart for About, so it doesn't need the
        # nested [[str]] list-of-lists shape.
        return {"text": [about_text] if about_text else []}

    if section == "experience":
        basic: list[list[str]] = []
        descriptions: list[list[str]] = []
        for ent_html in entities_html:
            esel = Selector(ent_html)
            texts = _entity_texts(ent_html)
            lis = esel.css("li").getall()
            if lis:
                # Multi-role company group: texts = [company, type+duration, location]
                company = texts[0] if texts else ""
                location = texts[2] if len(texts) > 2 else ""
                for li_html in lis:
                    li_texts = _entity_texts(li_html)
                    role = li_texts[0] if li_texts else ""
                    dates = li_texts[1] if len(li_texts) > 1 else ""
                    desc_lines = li_texts[2:-1] if len(li_texts) > 2 else []
                    skills_line = li_texts[-1] if len(li_texts) > 1 else ""
                    if role:
                        basic.append([role, company, dates, location])
                        skills_line = _normalize_skills(skills_line)
                        combined = desc_lines + ([skills_line] if skills_line else [])
                        descriptions.append(combined if combined else [""])
            else:
                # Single-role entry: texts = [role, company+type, dates, location, ...desc..., skills?]
                role = texts[0] if texts else ""
                raw_company = texts[1] if len(texts) > 1 else ""
                company = raw_company.split(" · ")[0] if " · " in raw_company else raw_company
                dates = texts[2] if len(texts) > 2 else ""
                location = texts[3] if len(texts) > 3 else ""
                # texts[4:-1] are description lines; texts[-1] is the skills line when it ends
                # with "aptitudes más" or similar — guard against index overlap (len<=4 means no desc).
                if len(texts) > 5:
                    desc_lines = texts[4:-1]
                    skills_line = texts[-1]
                elif len(texts) == 5:
                    # Could be just a skills line with no description, or a description with no skills.
                    last = texts[4]
                    if "aptitudes" in last.lower() or "aptitud" in last.lower():
                        desc_lines = []
                        skills_line = last
                    else:
                        desc_lines = [last]
                        skills_line = ""
                else:
                    desc_lines = []
                    skills_line = ""
                if role:
                    basic.append([role, company, dates, location])
                    skills_line = _normalize_skills(skills_line)
                    combined = desc_lines + ([skills_line] if skills_line else [])
                    descriptions.append(combined if combined else [""])
        return {"basic": basic, "description": descriptions}

    if section == "education":
        basic = []
        descriptions = []
        for ent_html in entities_html:
            texts = _entity_texts(ent_html)
            institution = texts[0] if texts else ""
            degree = texts[1] if len(texts) > 1 else ""
            dates = texts[2] if len(texts) > 2 else ""
            extra = texts[3:] if len(texts) > 3 else [""]
            if institution:
                basic.append([institution, degree, dates])
                descriptions.append(extra if extra else [""])
        return {"basic": basic, "description": descriptions}

    if section == "certifications":
        basic = []
        descriptions = []
        for ent_html in entities_html:
            texts = _entity_texts(ent_html)
            title = texts[0] if texts else ""
            issuer = texts[1] if len(texts) > 1 else ""
            dates = texts[2] if len(texts) > 2 else ""
            cred_id = texts[3] if len(texts) > 3 else ""
            extra = texts[4:] if len(texts) > 4 else [""]
            if title:
                basic.append([title, issuer, cred_id])
                descriptions.append([dates] + (extra if extra else [""]))
        return {"basic": basic, "description": descriptions}

    if section == "projects":
        basic_list = []
        descriptions = []
        skills_list = []
        for ent_html in entities_html:
            texts = _entity_texts(ent_html)
            name = texts[0] if texts else ""
            dates = texts[1] if len(texts) > 1 else ""
            desc = texts[2] if len(texts) > 2 else ""
            skills = texts[3] if len(texts) > 3 else ""
            if name:
                basic_list.append([name, dates])
                descriptions.append([desc] if desc else [""])
                skills_list.append([skills] if skills else [""])
        return {"basic": basic_list, "description": descriptions, "skills": skills_list}

    if section == "languages":
        langs = []
        for ent_html in entities_html:
            texts = _entity_texts(ent_html)
            lang = texts[0] if texts else ""
            proficiency = texts[1] if len(texts) > 1 else ""
            if lang:
                langs.append([lang, proficiency])
        return {"languages": langs}

    if section == "featured":
        # Featured items are identified by FeFeaturedItemUrn componentkey attributes.
        # They appear in pairs (same HTML duplicated); take every other one to deduplicate.
        featured_item_els = sel.xpath('//*[starts-with(@componentkey, "FeFeaturedItemUrn")]').getall()
        # Noise tokens to drop: reaction counts, comment counts, badges, type labels.
        _NOISE_PREFIXES = (
            "recomendación",
            "recommendation",
            "certificación",
            "certificacion",
        )
        _NOISE_PATTERNS = re.compile(
            r"^\d+,?\s*(número de reacciones|reactions?)"  # "10, número de reacciones10"
            r"|comentario"  # "1 comentario(s)"
            r"|·\s*\d+[a-z°]+"  # "· 1er" connection badge
            r"|destacado con premium"  # premium badge
            r"|número de reacciones",
            re.IGNORECASE,
        )
        _TYPE_LABELS = {"enlace", "link", "publicación", "publication", "contenido multimedia"}
        title_texts = []
        for i, el_html in enumerate(featured_item_els):
            if i % 2 != 0:
                # Duplicate — skip
                continue
            item_soup = bs(el_html, features="lxml")
            for hidden in item_soup.select(".visually-hidden"):
                hidden.decompose()
            ps = item_soup.find_all("p")
            raw_texts = [p.get_text(" ").strip() for p in ps]
            raw_texts = [t for t in raw_texts if t]

            if not raw_texts:
                continue

            # The first p is the type label.
            item_type = raw_texts[0].lower()
            if any(item_type.startswith(prefix) for prefix in _NOISE_PREFIXES):
                # Skip recommendations and certifications — they belong to other sections.
                continue

            # Collect clean lines, dropping the type label and noise.
            clean_lines = []
            for txt in raw_texts[1:]:
                if _NOISE_PATTERNS.search(txt):
                    continue
                if txt.lower() in _TYPE_LABELS:
                    continue
                if "anuncio" in txt.lower() or "publicidad" in txt.lower():
                    continue
                clean_lines.append(txt)

            # Attach URL if present (LinkedIn redirect link → extract real URL).
            links = item_soup.find_all("a", href=True)
            url = ""
            for lnk in links:
                href = lnk.get("href", "")
                if "linkedin.com/safety/go" in href:
                    m = re.search(r"url=([^&]+)", href)
                    if m:
                        import urllib.parse

                        url = urllib.parse.unquote(m.group(1))
                    break
                if href.startswith("http") and "linkedin.com" not in href:
                    url = href
                    break

            if url and url not in clean_lines:
                clean_lines.append(url)

            if clean_lines:
                title_texts.append(clean_lines)

        return {"title": title_texts}

    return {}


def markdownify(template_name: str = "peppermint.md", json_path: str | None = None) -> None:
    with open("selectors.json", encoding="utf-8") as f:
        to_extract = json.load(f)

    extracted: dict[str, Any] = {}
    for key in list(to_extract.keys()):
        if key.startswith("_"):
            continue
        extracted[key] = {}
        source = source_override.get(key, key)
        try:
            with open(f"data/{source}.html", encoding="utf-8") as html_content:
                html = html_content.read()
        except FileNotFoundError:
            print(f"Warning: data/{source}.html not found, skipping {key}")
            for item in to_extract[key].items():
                if isinstance(item[1], str):
                    extracted[key][item[0]] = []
            continue

        if _is_new_layout(html):
            extracted[key] = _extract_new_layout(key, html)
            continue

        selector = Selector(html)
        for item in to_extract[key].items():
            if not isinstance(item[1], str):
                continue
            try:
                # Support XPath selectors (starting with // or () in addition to CSS.
                if item[1].startswith("//") or item[1].startswith("("):
                    res = selector.xpath(item[1]).getall()
                else:
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
            if key == "about" and item[0] == "text":
                # Keep the shape consistent with _extract_new_layout("about", ...),
                # which returns a flat [str] (max one entry) for about.text — both
                # templates render it as `{{ about.text[0] }}` expecting a string.
                # The generic loop above otherwise builds list[list[str]] per matched
                # element, which would leak a Python list into the rendered Markdown
                # if this legacy path is ever exercised for "about". Flatten: join each
                # matched element's lines into one paragraph, then join multiple
                # matched elements as separate paragraphs.
                paragraphs = [" ".join(lines) for lines in res if lines]
                flattened = "\n\n".join(paragraphs)
                extracted[key] |= {item[0]: [flattened] if flattened else []}
            else:
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

    print(f"Results saved in {os.path.abspath('output.md')}")
    if json_path:
        print(f"Extracted data saved in {os.path.abspath(json_path)}")
