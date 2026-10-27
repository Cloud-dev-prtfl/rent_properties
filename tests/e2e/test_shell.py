"""M0 smoke journey: the shell page renders, is keyboard-navigable and has no serious axe issues.

Run against the compose stack with `make e2e`.
One-time setup: `uv sync --group e2e && uv run playwright install chromium`.
"""

import os

import pytest

pytest.importorskip("playwright")
from axe_playwright_python.sync_playwright import Axe

BASE_URL = os.environ.get("E2E_BASE_URL", "")
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not BASE_URL, reason="E2E_BASE_URL not set"),
]


@pytest.mark.parametrize("width", [360, 1280])
def test_shell_page_is_accessible(page, width):
    page.set_viewport_size({"width": width, "height": 800})
    page.goto(BASE_URL + "/")
    assert page.get_by_role("heading", level=1).is_visible()
    assert page.get_by_role("navigation", name="Main").is_visible()

    results = Axe().run(page)
    serious = [v for v in results.response["violations"] if v["impact"] in {"serious", "critical"}]
    assert serious == [], serious


def test_skip_link_is_first_tab_stop_and_moves_focus_to_main(page):
    page.goto(BASE_URL + "/")
    page.keyboard.press("Tab")
    skip = page.get_by_role("link", name="Skip to main content")
    assert skip.evaluate("el => el === document.activeElement")
    page.keyboard.press("Enter")
    assert page.evaluate("document.activeElement.id") == "main"
