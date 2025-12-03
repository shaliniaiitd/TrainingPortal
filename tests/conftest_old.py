import os
import sys
import logging
import pytest
from playwright.sync_api import sync_playwright


import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import os
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"



@pytest.fixture
def api_client():
    """Returns a DRF APIClient instance."""
    return APIClient()

@pytest.fixture
def auth_client(api_client, db):
    #db(built in fixture- gets db access to Django's User model  '
    """
    Creates a superuser, generates a JWT token, and returns
    an authenticated API client.
    """
    User = get_user_model()
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123"
    )

    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    # Authenticate APIClient with JWT token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

import pytest
from playwright.sync_api import Playwright
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

"""For unauthenticated tests if any to be conducted, right now not in use"""
@pytest.fixture
def api_context(playwright: Playwright):
    """Unauthenticated Playwright API client."""
    return playwright.request.new_context(base_url="http://localhost:8000")


@pytest.fixture
def auth_context(playwright: Playwright, db):
    """Authenticated Playwright API client using JWT."""
    User = get_user_model()

    user = User.objects.create_superuser(
        username="admin2",
        email="admin@example.com",
        password="admin123"
    )

    # Generate JWT
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    return playwright.request.new_context(
        base_url="http://localhost:8000",
        extra_http_headers={
            "Authorization":f"Bearer {access}",
            "Content-Type": "application/json"
        }
    )



# Prevent Django from detecting Playwright's event loop during DB setup

def pytest_configure(config):
    # Disable any plugin that starts an event loop
    for plugin in ["pytest_asyncio", "pytest_trio", "pytest_tornasync"]:
        if plugin in config.pluginmanager.list_plugin_distinfo():
            config.pluginmanager.set_blocked(plugin)


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
