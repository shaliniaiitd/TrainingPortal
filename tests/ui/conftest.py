import os
import sys
import logging
import pytest
from playwright.sync_api import sync_playwright


def _find_repo_root(start_path: str, markers=None) -> str:
    """Search upwards from start_path for repo root indicators and return path.

    Looks for any filename/dir in `markers` (default: manage.py, .git, pyproject.toml).
    Falls back to two levels up if nothing found.
    """
    if markers is None:
        markers = ("manage.py", ".git", "pyproject.toml", "requirements.txt")

    cur = os.path.abspath(start_path)
    root = os.path.abspath(os.sep)
    while True:
        for m in markers:
            if os.path.exists(os.path.join(cur, m)):
                return cur
        if cur == root:
            # fallback to two levels up from this conftest file
            return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cur = os.path.abspath(os.path.join(cur, ".."))


# Make test package importable regardless of working directory.
repo_root = _find_repo_root(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

try:
    from tests.ui.pages import PageFactory
except Exception as exc:  # pragma: no cover - helpful runtime diagnostic
    logging.error(
        "Failed to import PageFactory from tests.ui.pages. repo_root=%s sys.path[0]=%s error=%s",
        repo_root,
        sys.path[0] if sys.path else None,
        exc,
    )
    # Re-raise with clearer message for CI / developer
    raise ImportError(
        "Could not import 'tests.ui.pages.PageFactory'. Ensure the repository root contains the 'tests' directory "
        "and that pytest is running from the project root. repo_root=%s" % repo_root
    ) from exc


@pytest.fixture(scope="session")
def playwright_instance():
    """Session-scoped Playwright instance"""
    with sync_playwright() as p:
        yield p


@pytest.fixture
def page(playwright_instance):
    """Create a fresh browser page for each test."""
    browser = playwright_instance.chromium.launch(headless = False)
    page = browser.new_page()
    yield page
    browser.close()


@pytest.fixture
def factory():
    """Provide PageFactory class"""
    return PageFactory
