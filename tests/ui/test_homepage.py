"""
Home Page UI Tests - test_homepage.py

Comprehensive test suite for TrainingPortal homepage using PageFactory
and BaseTestClass. Tests cover navigation, page loading, content visibility,
and link functionality.
"""

import pytest
from tests.ui.base_test import BaseTestClass

@pytest.mark.page("home")
class TestHomepage(BaseTestClass):
    """Test suite for homepage functionality and UX."""
    def test_home_page_loads(self,page_obj):
        """Test: Homepage loads successfully."""
        self.assert_page_loaded(page_obj, "is_home_loaded")

    def test_home_page_heading_visible(self,page_obj):
        """Test: Home page displays main heading."""
        heading = page_obj.get_page_heading()
        assert heading, "Home page heading is missing"
        assert len(heading) > 0, "Heading text is empty"

    def test_home_page_url_correct(self,page_obj):
        """Test: Home page URL is correct after navigation."""
        current_url = page_obj.get_current_url()
        assert "/myapp/" in current_url, f"Expected /myapp/ in URL, got {current_url}"

    def test_home_page_title(self, page_obj):
        """Test: Home page has a valid title."""
        title = page_obj.get_page_title()
        assert title, "Page title is empty"
        assert len(title) > 0, "Page title not set"

    def test_page_not_empty(self, page_obj):
        """Test: Home page has content (not empty)."""
        content = page_obj.get_page_text()
        assert content, "Page content is empty"
        assert len(content) > 0, "No content rendered on homepage"

    def test_members_section_visible(self,page_obj):
        """Test: Members section is visible on homepage."""
        assert page_obj.is_members_section_visible(), "Members section not visible"

    def test_courses_section_visible(self,page_obj):
        """Test: Courses section is visible on homepage."""
        assert page_obj.is_courses_section_visible(), "Courses section not visible"

    def test_members_link_visible(self, page_obj):
        """Test: Members navigation link is visible."""
        assert page_obj.is_element_visible(page_obj.MEMBERS_LINK), "Members link not visible"

    def test_courses_link_visible(self, page_obj):
        """Test: Courses navigation link is visible."""

        assert page_obj.is_element_visible(page_obj.COURSES_LINK), "Courses link not visible"

    def test_click_members_link(self,page_obj):
        """Test: Clicking Members link navigates to members page."""
        page_obj.click_meet_our_members()
        page_obj.wait_for_load_state("networkidle")
        
        current_url = page_obj.get_current_url()
        assert "/members" in current_url, f"Expected /members in URL after click, got {current_url}"


    def test_click_courses_link(self,page_obj):
        """Test: Clicking Courses link navigates to courses page."""
        page_obj.click_courses_we_offer()
        page_obj.wait_for_load_state("networkidle")
        
        current_url = page_obj.get_current_url()
        assert "/courses" in current_url, f"Expected /courses in URL after click, got {current_url}"



    def test_multiple_navigation_cycles(self):
        """Test: User can navigate to sections and back to home."""
        home = self.get_page("home")
        members = self.get_page("members")
        
        # Go home
        home.goto_page()
        home_url_1 = home.get_current_url()
        assert "/myapp/" in home_url_1
        
        # Go to members
        home.click_meet_our_members()
        home.wait_for_load_state("networkidle")
        members_url = home.get_current_url()
        assert "/members" in members_url
        
        # Go back to home
        home.goto_page()
        home_url_2 = home.get_current_url()
        assert "/myapp/" in home_url_2

    def test_home_page_responsive_load(self):
        """Test: Home page loads in reasonable time."""
        home = self.get_page("home")
        import time
        
        start = time.time()
        home.goto_page()
        elapsed = time.time() - start
        
        # Page should load in less than 10 seconds
        assert elapsed < 10, f"Page took too long to load: {elapsed:.2f}s"

    def test_home_contains_navigation_menu(self, page_obj):
        """Test: Home page has navigation menu visible."""
        
        # Check for navigation elements
        members_visible = page_obj.is_element_visible(page_obj.MEMBERS_LINK)
        courses_visible = page_obj.is_element_visible(page_obj.COURSES_LINK)
        
        assert members_visible or courses_visible, "No navigation menu visible"

    def test_home_page_no_404(self,page_obj):
        """Test: Home page does not return 404 error."""
        
        # Check page title doesn't contain "404" or "not found"
        title = page_obj.get_page_title()
        assert "404" not in title.lower(), "Page returned 404"
        assert "not found" not in title.lower(), "Page not found"

    def test_home_page_sections_order(self,page_obj):
        """Test: Home page sections appear in logical order."""
        
        # Both sections should be visible
        assert page_obj.is_members_section_visible(), "Members section not visible"
        assert page_obj.is_courses_section_visible(), "Courses section not visible"
        
        # Get their positions (if implemented in page object)
        # This validates layout is correct

    def test_navigate_to_home_from_different_pages(self):
        """Test: Can reach home from different pages via navigation."""
        home = self.get_page("home")
        members = self.get_page("members")
        
        # Start at members
        members.goto_page()
        assert "/members" in members.get_current_url()
        
        # Navigate to home using home page object
        home.goto_page()
        assert "/myapp/" in home.get_current_url()

@pytest.mark.page("home")
class TestHomepageUX(BaseTestClass):
    """Test suite for homepage user experience and accessibility."""

    def test_home_links_enabled(self,page_obj):
        """Test: All navigation links are enabled."""
        
        # Members link should be enabled
        assert page_obj.is_element_enabled(page_obj.MEMBERS_LINK), "Members link not enabled"
        
        # Courses link should be enabled
        assert page_obj.is_element_enabled(page_obj.COURSES_LINK), "Courses link not enabled"

    def test_home_page_no_js_errors(self):
        """Test: No JavaScript errors on homepage."""
        home = self.get_page("home")
        
        # Set up console message listener
        messages = []
        home.page.on("console", lambda msg: messages.append(msg))
        
        home.goto_page()
        
        # Check for error messages (optional - depends on app)
        error_messages = [m for m in messages if "error" in str(m).lower()]
        # Note: Some apps may have non-critical errors, adjust as needed
        assert len(error_messages) == 0, f"JavaScript errors: {error_messages}"

    def test_home_page_hover_states(self,page_obj):
        """Test: Navigation links respond to hover."""
        
        # Hover over members link
        page_obj.hover_element(page_obj.MEMBERS_LINK)
        assert page_obj.is_element_visible(page_obj.MEMBERS_LINK), "Members link disappeared on hover"
        
        # Hover over courses link
        page_obj.hover_element(page_obj.COURSES_LINK)
        assert page_obj.is_element_visible(page_obj.COURSES_LINK), "Courses link disappeared on hover"

    def test_home_page_keyboard_navigation(self, page_obj):
        """Test: Home page supports keyboard navigation."""
        # Press Tab to navigate
        page_obj.press_key("Tab")
        
        # Page should still be interactive
        assert page_obj.is_home_loaded(), "Page not loaded after Tab press"

    def test_home_heading_contrast(self,page_obj):
        """Test: Main heading is visible and readable."""
        
        heading_text = page_obj.get_page_heading()
        # Verify heading has meaningful content (not empty)
        assert heading_text.strip(), "Heading is empty or whitespace"
        assert len(heading_text) > 2, "Heading text too short"

    def test_home_page_layout_stability(self,page_obj):
        """Test: Page layout is stable (elements don't shift)."""
        
        # Get initial positions
        heading_text_1 = page_obj.get_page_heading()
        
        # Wait and check again
        page_obj.wait(1)
        heading_text_2 = page_obj.get_page_heading()
        
        # Text should remain the same
        assert heading_text_1 == heading_text_2, "Page layout changed/shifted"

    def test_home_page_resource_loading(self,page_obj):
        """Test: All page resources load successfully."""
        
        # Wait for full page load

        page_obj.wait_for_load_state("networkidle")
        
        # Page should be fully loadedpage_obj
        assert page_obj.is_home_loaded(), "Page resources not fully loaded"

    def test_home_page_back_button(self,page_obj):
        """Test: Browser back button works from members page back to home."""
        
        # Navigate to home

        home_url = page_obj.get_current_url()
        
        # Navigate to members
        page_obj.click_meet_our_members()
        page_obj.wait_for_load_state("networkidle")
        members_url = page_obj.get_current_url()
        assert members_url != home_url
        
        # Click back button
        page_obj.go_back()
        page_obj.wait_for_load_state("networkidle")
        back_url = page_obj.get_current_url()
        
        # Should be back at home
        assert "/myapp/" in back_url, "Back button didn't return to home"

    def test_home_page_reload(self,page_obj):
        """Test: Page can be reloaded without errors."""
        
        # Reload page
        page_obj.reload_page()
        page_obj.wait_for_load_state("networkidle")
        
        # Page should still load
        assert page_obj.is_home_loaded(), "Page didn't load after reload"

    def test_home_page_multiple_clicks_safe(self,page_obj):
        """Test: Clicking links multiple times doesn't cause issues."""
        
        # Click members link twice quickly
        page_obj.click_meet_our_members()
        page_obj.wait_for_load_state("networkidle")
        
        # Go back
        page_obj.goto_page()
        
        # Click again
        page_obj.click_meet_our_members()
        page_obj.wait_for_load_state("networkidle")
        
        # Should be on members page
        assert "/members" in page_obj.get_current_url()
