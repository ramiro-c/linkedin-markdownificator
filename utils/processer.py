from utils.lib import *

def repeated_string(s):
    half = len(s)//2
    return s[:half] if s[half:] == s[:half] else s


# This dictionary contains CSS selectors for the actual content
to_extract = {
              "main":           {"name":        "h1",
                                 "description": "div > div.scaffold-layout.scaffold-layout--breakpoint-xl.scaffold-layout--main-aside.scaffold-layout--reflow.pv-profile.pvs-loader-wrapper__shimmer--animate > div > div > main > section > div.ph5 > div.mt2.relative > div:nth-child(1) > div.text-body-medium.break-words",
                                 "main_skills": "div > div.scaffold-layout.scaffold-layout--breakpoint-xl.scaffold-layout--main-aside.scaffold-layout--reflow.pv-profile.pvs-loader-wrapper__shimmer--animate > div > div > main > section:nth-child(4) > div:nth-child(4) > div > ul > li > div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > div > div:nth-child(2)"},
               "featured":       {"title":       ".pv-profile-component-builder__card [class*=\"inline-show-more-text\"]",
                                  "description": ".pv-profile-component-builder__card [class*=\"inline-show-more-text\"]"},
              "experience":     {"basic" :      "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between",
                                 "description": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > ul > li:nth-child(1) > div > ul > li > div"},
              "education":      {"basic" :      "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > a",
                                 "description": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > a"},
               "certifications": {"basic":       "section.artdeco-card.pb3 .display-flex.flex-column.full-width",
                                  "dates":       "section.artdeco-card.pb3 span.pvs-entity__caption-wrapper",
                                  "description": "section.artdeco-card.pb3 .pvs-entity__sub-components"},
              "projects":       {"basic" :      "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > div > div > div > div",
                                 "description": "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > ul > li:nth-child(1)",
                                 "skills":      "div > div > div.display-flex.flex-column.align-self-center.flex-grow-1 > div > ul > li:nth-child(2)"},

               "volunteering":   {"basic":       "#volunteering_experience ~ div ul li.artdeco-list__item div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between",
                                  "description": "#volunteering_experience ~ div ul li.artdeco-list__item div.pvs-entity__sub-components"},
               "languages":      {"languages":   "section.artdeco-card.pb3 .display-flex.flex-column.full-width"}
}



# Keys whose data lives inside another file (e.g. volunteering is in main.html)
source_override = {"volunteering": "main"}

def markdownify():
    extracted = {}
    for key in list(to_extract.keys()):
        extracted[key] = {}
        source = source_override.get(key, key)
        with open(f"data/{source}.html", encoding="utf-8") as html_content:
            selector = Selector(html_content.read())

        for item in to_extract[key].items():
            if type(item[1]) == str:
                res = selector.css(item[1]).getall()
                for index in range(len(res)):
                    soup = bs(res[index], features="lxml")
                    for br in soup.find_all("br"):
                        br.replace_with("\n")
                    text = soup.get_text().strip()
                    res[index] = text.split('\n')
                    res[index] = [repeated_string(item) for item in res[index] if item.strip()]
                extracted[key] |= {item[0]: res}

    # Save raw extracted data in a file        
    # with open("data/extracted.md", "w", encoding="utf-8") as f:
    #     for item in extracted.items():
    #         f.write(f"# {item[0]}\n")
    #         for subitem in item[1].items():
    #             f.write(f"## {subitem[0]}\n{subitem[1]}\n")
    #         f.write("\n")
    #     f.close

    # Load template
    # Environment([globals={'zip': zip}])
    template_loader = FileSystemLoader(searchpath="./templates")  # Assuming templates are in the same directory
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("peppermint.md") # Define template

    # Render and write output
    output_text = template.render(extracted, zip=zip, len=len)  

    with open("output.md", "w", encoding="utf-8") as out:
        out.write(output_text)
