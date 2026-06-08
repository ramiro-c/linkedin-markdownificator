"""Integration tests for the full markdownify() pipeline."""

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Set up a temporary workspace with selectors.json, data/, and templates/."""
    selectors: dict[str, Any] = {
        "main": {
            "name": "h1",
        },
    }
    (tmp_path / "selectors.json").write_text(json.dumps(selectors))

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "main.html").write_text("<html><body><h1>John Doe</h1></body></html>")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "peppermint.md").write_text("{% for name in main.name %}{{ name[0] }}{% endfor %}")

    return tmp_path


def test_markdownify_produces_output(temp_workspace: Path) -> None:
    """markdownify() should create output.md with extracted content."""
    from processer import markdownify  # noqa: PLC0415

    cwd = Path.cwd()
    try:
        os.chdir(temp_workspace)
        markdownify()

        output = temp_workspace / "output.md"
        assert output.exists()
        assert "John Doe" in output.read_text()
    finally:
        os.chdir(cwd)


def test_markdownify_handles_br_and_visually_hidden(temp_workspace: Path) -> None:
    """<br> should become newlines; .visually-hidden should be stripped."""
    selectors: dict[str, Any] = {
        "main": {
            "description": "p",
        },
    }
    (temp_workspace / "selectors.json").write_text(json.dumps(selectors))

    data_dir = temp_workspace / "data"
    (data_dir / "main.html").write_text(
        '<html><body><p>Line1<br>Line2<span class="visually-hidden">hidden</span></p></body></html>'
    )

    (temp_workspace / "templates" / "peppermint.md").write_text(
        "{% for desc in main.description %}{{ desc | join(' ') }}{% endfor %}"
    )

    from processer import markdownify  # noqa: PLC0415

    cwd = Path.cwd()
    try:
        os.chdir(temp_workspace)
        markdownify()

        content = (temp_workspace / "output.md").read_text()
        assert "Line1" in content
        assert "Line2" in content
        assert "hidden" not in content
    finally:
        os.chdir(cwd)


def test_markdownify_with_json_export(temp_workspace: Path) -> None:
    """When json_path is set, markdownify() should write the extracted JSON."""
    from processer import markdownify  # noqa: PLC0415

    cwd = Path.cwd()
    try:
        os.chdir(temp_workspace)
        json_path = str(temp_workspace / "extracted.json")
        markdownify(json_path=json_path)

        assert os.path.isfile(json_path)
        data: dict[str, Any] = json.loads(Path(json_path).read_text())
        assert data["main"]["name"] == [["John Doe"]]
    finally:
        os.chdir(cwd)


def test_markdownify_handles_missing_html(temp_workspace: Path, capsys: Any) -> None:
    """When a data file is missing, markdownify should warn and keep going."""
    selectors: dict[str, Any] = {
        "main": {"name": "h1"},
        "featured": {"title": "h2"},
    }
    (temp_workspace / "selectors.json").write_text(json.dumps(selectors))

    data_dir = temp_workspace / "data"
    (data_dir / "main.html").write_text("<html><body><h1>John Doe</h1></body></html>")
    # featured.html intentionally not created

    from processer import markdownify  # noqa: PLC0415

    cwd = Path.cwd()
    try:
        os.chdir(temp_workspace)
        markdownify()

        captured = capsys.readouterr()
        assert "Warning: data/featured.html not found" in captured.out

        output = temp_workspace / "output.md"
        assert output.exists()
    finally:
        os.chdir(cwd)
