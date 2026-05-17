from jinja2 import Environment, FileSystemLoader
import pytest

env = Environment(loader=FileSystemLoader("templates"))

mock = {
    "main": {
        "name": [["John Doe"]],
        "description": [["Software engineer"]],
        "main_skills": [["React, Python"]],
    },
    "featured": {
        "title": [["Post one content\n\nwith multiple lines", "Post two content"]],
    },
    "experience": {
        "basic": [["Company Inc", "Full-time", "2020 - present"]],
        "description": [["Did stuff\n\nMore details", "React, Python"]],
    },
    "education": {
        "basic": [["UTN", "Engineering", "2018 - 2023"]],
        "description": [["University name\n\nDegree\ngpa", "2018 - 2023"]],
    },
    "certifications": {
        "basic": [["AWS Certified"]],
        "dates": [["2024"]],
        "description": [["Some desc"]],
    },
    "projects": {
        "basic": [["My Project"]],
        "description": [["Project desc"]],
        "skills": [["React, Node"]],
    },
    "volunteering": {
        "basic": [["Helper", "Org", "2021", "Education"]],
        "description": [["Helped students"]],
    },
    "languages": {
        "languages": [["Spanish", "Native"], ["English", "Advanced"]],
    },
}


@pytest.mark.parametrize("template_name", ["default_template.md", "peppermint.md"])
def test_template_renders_without_error(template_name):
    template = env.get_template(template_name)
    result = template.render(mock, zip=zip, len=len)
    assert "John Doe" in result
    assert "Company Inc" in result
    assert "UTN" in result
    assert "AWS Certified" in result
    assert "My Project" in result
    assert "Helper" in result
    assert "Spanish" in result


@pytest.mark.parametrize("template_name", ["default_template.md", "peppermint.md"])
def test_template_no_html_tags(template_name):
    template = env.get_template(template_name)
    result = template.render(mock, zip=zip, len=len)
    assert "<h3" not in result
    assert "<p " not in result
    assert "<small" not in result
    assert "</h3>" not in result
    assert "</p>" not in result
    assert "</small>" not in result
