"""Unit tests for _extract_new_layout("main"/"about", ...) — About text and pinned/top skills.

Fixtures mirror the real post-2025 LinkedIn React/SDUI DOM shape confirmed by a live
scrape (see the implementation plan): About and "Principales aptitudes"/"Top skills"
(pinned skills) live inside the *same* componentkey card ending in the case-sensitive
substring "About" — which naturally excludes the lowercase "<slug>_about_edit" edit
button and the unrelated footer "Acerca de"/"About LinkedIn" link
(href="https://about.linkedin.com/"). Both About and the skills line are plain <p>
tags; the skills line itself is already "•"-joined (no pill/list markup).
"""

import sys

sys.path.insert(0, "utils")

from processer import _extract_new_layout  # noqa: E402


def _wrap(main_card: str, footer: str = "") -> str:
    return f"""
    <html><body>
    <main id="workspace">
      <h2>John Doe</h2>
      <p>Verified badge</p>
      <p>Software Engineer</p>
      <section>
        {main_card}
      </section>
    </main>
    {footer}
    </body></html>
    """


ABOUT_WITH_NESTED_FOOTER_CARD = """
    <div id="card1" componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
      <section componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
        <div>
          <footer class="nested-footer">
            <nav>
              <a href="https://about.linkedin.com/">
                <p>Acerca de</p>
              </a>
            </nav>
          </footer>
          <div>
            <div>
              <h2>Acerca de</h2>
              <div><a componentkey="john-doe_about_edit" href="/edit/">edit</a></div>
            </div>
            <div>
              <p><span data-testid="expandable-text-box">About paragraph one.<br><br>About paragraph two.<button>ver más</button></span></p>
            </div>
          </div>
        </div>
      </section>
    </div>
    """

FOOTER_ONLY_CARD = """
    <div id="card1" componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
      <section componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
        <footer class="nested-footer">
          <nav>
            <a href="https://about.linkedin.com/">
              <p>Acerca de</p>
            </a>
          </nav>
        </footer>
      </section>
    </div>
    """

ABOUT_AND_SKILLS_CARD = """
    <div id="card1" componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
      <section componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
        <div>
          <div>
            <div>
              <h2>Acerca de</h2>
              <div><a componentkey="john-doe_about_edit" href="/edit/">edit</a></div>
            </div>
            <div>
              <p><span data-testid="expandable-text-box">About paragraph one.<br><br>About paragraph two.<button>ver más</button></span></p>
              <div>
                <div>
                  <div>
                    <div>
                      <p>Principales aptitudes</p>
                      <p>React.js &bull; Node.js &bull; Python</p>
                    </div>
                  </div>
                  <a href="https://www.linkedin.com/in/john-doe/overlay/top-skills-details/">arrow</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
    """

ABOUT_ONLY_CARD = """
    <div id="card1" componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
      <section componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
        <div>
          <div>
            <div>
              <h2>Acerca de</h2>
              <div><a componentkey="john-doe_about_edit" href="/edit/">edit</a></div>
            </div>
            <div>
              <p><span data-testid="expandable-text-box">Just one paragraph, no skills.</span></p>
            </div>
          </div>
        </div>
      </section>
    </div>
    """

SKILLS_ONLY_CARD = """
    <div id="card1" componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
      <section componentkey="com.linkedin.sdui.profile.card.refXYZAbout">
        <div>
          <div>
            <div>
              <p>Principales aptitudes</p>
              <p>Go &bull; Rust</p>
            </div>
          </div>
        </div>
      </section>
    </div>
    """


def test_main_extracts_pinned_skills() -> None:
    html = _wrap(ABOUT_AND_SKILLS_CARD)
    result = _extract_new_layout("main", html)
    assert result["main_skills"] == [["React.js • Node.js • Python"]]
    assert result["name"] == [["John Doe"]]
    assert result["description"] == [["Software Engineer"]]


def test_main_no_pinned_skills_returns_stub() -> None:
    html = _wrap(ABOUT_ONLY_CARD)
    result = _extract_new_layout("main", html)
    assert result["main_skills"] == [[""]]


def test_about_extracts_real_text() -> None:
    html = _wrap(ABOUT_AND_SKILLS_CARD)
    result = _extract_new_layout("about", html)
    assert result == {"text": ["About paragraph one.\n\nAbout paragraph two."]}


def test_about_missing_returns_empty_list() -> None:
    html = _wrap(SKILLS_ONLY_CARD)
    result = _extract_new_layout("about", html)
    assert result == {"text": []}


def test_no_about_or_skills_card_at_all() -> None:
    html = _wrap("")
    assert _extract_new_layout("about", html) == {"text": []}
    assert _extract_new_layout("main", html)["main_skills"] == [[""]]


def test_footer_trap_excluded_real_about_wins() -> None:
    """A <footer> nested *inside* the matched About card's own subtree (simulating
    the hypothetical future markup shift the implementation's docstring warns
    about) must be stripped by footer.decompose(). The footer's 'Acerca de' <p>
    sits before the real About paragraph in document order, so without the
    decompose call it would be picked up as the About text instead."""
    html = _wrap(ABOUT_WITH_NESTED_FOOTER_CARD)
    result = _extract_new_layout("about", html)
    assert result["text"] == ["About paragraph one.\n\nAbout paragraph two."]
    assert "about.linkedin.com" not in "".join(result["text"])
    assert "Acerca de" not in "".join(result["text"])


def test_footer_trap_alone_produces_no_about() -> None:
    """If the matched About card's only <p> content lives inside a nested <footer>
    (no real About paragraph anywhere in the card), it must be stripped by
    footer.decompose() and never surface as the About text."""
    html = _wrap(FOOTER_ONLY_CARD)
    result = _extract_new_layout("about", html)
    assert result == {"text": []}
