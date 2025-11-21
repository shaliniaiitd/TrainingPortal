"""Base Test Class for UI tests.

Provides common setup/teardown, fixtures, and utility methods
for all UI test classes. Demonstrates OOP hierarchy with inheritance.
"""

import pytest
from tests.ui.pages import PageFactory
from tests.ui.pages.page_factory import FormBuilder


class BaseTestClass:
    """Base class for all UI tests.

    Provides:
    - Fixture setup/teardown (via pytest)
    - Common page loading utilities
    - PageFactory access
    - FormBuilder access
    - Common assertions
    """

    @pytest.fixture
    def page_obj(self, request):
        marker = request.node.get_closest_marker("page")
        page_name = marker.args[0]
        page_id = marker.kwargs.get("id", None)

        page = self.get_page(page_name)

        if page_id is not None:
            page.goto_page(page_id)
        else:
            page.goto_page()

        return page


    @pytest.fixture(autouse=True)
    def setup_teardown(self, page):
        """Setup and teardown for each test."""
        # Setup
        self.page = page
        self.factory = PageFactory
        print(f"\n[SETUP] Starting test: {self.__class__.__name__}")

        yield  # Run the test

        # Teardown
        print(f"[TEARDOWN] Finished test: {self.__class__.__name__}")

    def get_page(self, page_name: str):
        """Convenience: get a page object by name using factory."""
        return self.factory.get_page(page_name, self.page)

    def build_form(self, name: str = "form") -> FormBuilder:
        """Convenience: create a fresh FormBuilder instance."""
        return FormBuilder(name)

    def assert_element_visible(self, selector: str, timeout_ms: int = 5000):
        """Assert that an element matching locator is visible."""
        try:
            self.page.locator(selector).wait_for(timeout=timeout_ms)
        except Exception as e:
            pytest.fail(f"Element '{selector}' not visible: {e}")

    def assert_text_visible(self, text: str, timeout_ms: int = 5000):
        """Assert that specific text is visible on page."""
        try:
            self.page.get_by_text(text).wait_for(timeout=timeout_ms)
        except Exception as e:
            pytest.fail(f"Text '{text}' not found: {e}")

    def assert_page_loaded(self, page_obj, method_name: str = "is_page_loaded"):
        """Assert that a page object page is loaded using its checker method."""
        if hasattr(page_obj, method_name):
            checker = getattr(page_obj, method_name)
            if callable(checker):
                assert checker(), f"{page_obj.__class__.__name__}.{method_name}() returned False"
            else:
                pytest.fail(f"{method_name} is not callable on {page_obj.__class__.__name__}")
        else:
            pytest.fail(f"{page_obj.__class__.__name__} has no method {method_name}")

    def assert_count_increased(self, before: int, after: int, delta: int = 1):
        """Assert that after count is at least 'delta' more than before."""
        assert after >= before + delta, f"Expected count to increase by {delta}: {before} -> {after}"

    def assert_count_decreased(self, before: int, after: int, delta: int = 1):
        """Assert that after count is at least 'delta' less than before."""
        assert after <= before - delta, f"Expected count to decrease by {delta}: {before} -> {after}"

    def wait_for_navigation(self, timeout_ms: int = 5000):
        """Wait for page navigation to complete."""
        self.page.wait_for_load_state("networkidle", timeout=timeout_ms)
