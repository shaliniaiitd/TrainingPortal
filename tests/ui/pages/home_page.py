"""
Home Page Object - represents the home/index page of TrainingPortal.
"""

from .base_page import BasePage


class HomePage(BasePage):
    """Page object for home page at /myapp/"""

    # Locators
    TITLE = "h1:has-text('CONNECT CHAMPS')"  # This must be visible for page to be considered loaded
    WELCOME_HEADING = "h1:has-text('Welcome to our company portal')"
    MEMBERS_SECTION = "text=Meet our Members"
    COURSES_SECTION = "text=Courses We Offer"
    MEMBERS_LINK = "a:has-text('Members')"
    COURSES_LINK = "a:has-text('Courses')"
    ABOUT_SECTION = "text=About"

    def goto_page(self) -> "HomePage":
        """Navigate to home page."""
        self.goto("/myapp/")
        return self

    def is_home_loaded(self) -> bool:
        """Check if home page is loaded."""
        return self.is_element_visible(self.TITLE)

    def click_meet_our_members(self) -> None:
        """Click on 'Meet our Members' section."""
        self.click_by_text("Members")

    def click_courses_we_offer(self) -> None:
        """Click on 'Courses We Offer' section."""
        self.click_by_text("Courses")

    def is_members_section_visible(self) -> bool:
        """Check if Members section is visible."""
        return self.is_element_visible(self.MEMBERS_SECTION)

    def is_courses_section_visible(self) -> bool:
        """Check if Courses section is visible."""
        return self.is_element_visible(self.COURSES_SECTION)

    def get_page_heading(self) -> str:
        """Get main page heading."""
        return self.get_element_text(self.TITLE)
