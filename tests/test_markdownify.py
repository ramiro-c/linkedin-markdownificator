import os
import sys
sys.path.insert(0, 'utils')

import pytest

from processer import markdownify


def data_files_exist():
    required = ["main", "featured", "experience", "education", "certifications", "projects", "languages"]
    return all(os.path.isfile(f"data/{f}.html") for f in required)


@pytest.mark.skipif(not data_files_exist(), reason="scraped HTML files not found in data/")
class TestMarkdownify:
    def test_runs_and_produces_output(self):
        markdownify()
        assert os.path.isfile("output.md")
        with open("output.md") as f:
            content = f.read()
        assert len(content) > 0

    def test_no_html_in_output(self):
        with open("output.md") as f:
            content = f.read()
        assert "<h3" not in content
        assert "<p " not in content
        assert "<small" not in content
        assert "</h3>" not in content
        assert "</p>" not in content
        assert "</small>" not in content
