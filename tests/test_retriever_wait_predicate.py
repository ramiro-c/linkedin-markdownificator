"""Regression guard for the Fix 1 bug: the hydration wait in scrape_section()'s
main-page branch (utils/retriever.py) must match componentkey="...About..."
case-sensitively, agreeing with utils/processer.py's _extract_about_and_skills(),
which reads `contains(@componentkey, "About")`. A case-insensitive match (the
trailing `i` flag on the querySelectorAll attribute selector) would also match
the lowercase "<slug>_about_edit" edit-button componentkey, letting the wait
resolve before the real About/skills card hydrates and silently saving
unhydrated HTML (the whole call is wrapped in contextlib.suppress(Exception),
so this would fail with no error at all).

Full Selenium/browser-level testing of the wait isn't practical here, so this
test settles for a cheap source-level check: it locates the actual
querySelectorAll componentkey selector embedded in retriever.py's source and
asserts it does not carry the case-insensitive ` i` flag.
"""

import re
from pathlib import Path

RETRIEVER_SRC_PATH = Path(__file__).resolve().parent.parent / "utils" / "retriever.py"


def _find_about_componentkey_selector(source: str) -> str:
    match = re.search(r"componentkey\*=\\\"About\\\"[^']*", source)
    assert match is not None, "expected an About componentkey selector in utils/retriever.py"
    return match.group(0)


def test_about_wait_predicate_matches_componentkey_case_sensitively() -> None:
    source = RETRIEVER_SRC_PATH.read_text(encoding="utf-8")
    selector = _find_about_componentkey_selector(source)

    # The case-insensitive attribute-selector flag is a literal " i" right before
    # the closing "]" of the CSS attribute selector, e.g. '[componentkey*="About" i]'.
    assert not re.search(r'"\s+i\s*\]', selector), (
        f"About componentkey wait predicate regained the case-insensitive 'i' flag: {selector!r}"
    )
