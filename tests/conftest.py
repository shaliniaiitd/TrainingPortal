import os
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

# Django sync safety override
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

################################################################################
#                               DRF CLIENTS and JWT Authentication
################################################################################

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, db):
    User = get_user_model()
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123"
    )
    api_client.force_authenticate(user)
    return api_client


################################################################################
#                               PLAYWRIGHT SYNC
################################################################################

from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p


################################################################################
#         🔥 APIRequestContext fixtures (for API tests (with django)) 🔥
################################################################################

@pytest.fixture
def context(playwright, db):
    """
    Unauthenticated API client using Playwright’s request.new_context().
    """
    return playwright.request.new_context(base_url="http://localhost:8000")


@pytest.fixture
def auth_context(playwright, db):
    """
    Authenticated API client compatible with async-style tests:
    auth_context.get(url=...) should work.
    """
    User = get_user_model()

    user = User.objects.create_superuser(
        username="admin2",
        email="admin2@example.com",
        password="admin123",
    )

    # manual JWT creation (Playwright only supports headers)
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    return playwright.request.new_context(
        base_url="http://localhost:8000",
        extra_http_headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    )


################################################################################
#                    🔥 UI FIXTURES (keep old behavior intact) 🔥
################################################################################

@pytest.fixture(scope="session")
def browser(playwright):
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    """
    UI test Page object.
    """
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
