"""
Course Detail Page Object - represents the detail view of a single course.
"""

from .base_page import BasePage


class CourseDetailPage(BasePage):
    """Page object for course detail page."""

    # Locators
    PAGE_HEADING = "h1, h2"
    COURSE_NAME_TEXT = "text=Course Name"
    COURSE_TYPE_TEXT = "text=Course Type"
    FACULTY_TEXT = "text=Faculty"
    DESCRIPTION_TEXT = "text=Description"
    DURATION_TEXT = "text=Duration"
    UPDATE_BTN = "a:has-text('Update'), button:has-text('Edit'), a:has-text('Edit')"
    DELETE_BTN = "a:has-text('Delete'), button:has-text('Delete')"
    BACK_BTN = "a:has-text('Back'), a:has-text('Back to Courses')"
    COURSE_INFO = ".course-info, .detail-view, [role='main']"

    def goto_course_detail(self, course_id: int) -> "CourseDetailPage":
        """Navigate to course detail page by course ID."""
        self.goto(f"/myapp/courses/{course_id}/")
        return self

    def is_detail_page_loaded(self) -> bool:
        """Check if detail page is loaded."""
        return self.is_element_visible(self.PAGE_HEADING)

    def get_course_name(self) -> str:
        """Get course name."""
        return self._get_field_value("Course Name")

    def get_course_type(self) -> str:
        """Get course type."""
        return self._get_field_value("Course Type")

    def get_faculty(self) -> str:
        """Get faculty name."""
        return self._get_field_value("Faculty")

    def get_description(self) -> str:
        """Get course description."""
        return self._get_field_value("Description")

    def get_duration(self) -> str:
        """Get course duration."""
        return self._get_field_value("Duration")

    def _get_field_value(self, field_name: str) -> str:
        """Helper to extract field value from detail view."""
        try:
            # Try to find label followed by value
            locator = self.page.locator(f"text='{field_name}' >> following-sibling::*")
            if locator.count() > 0:
                return locator.text_content().strip()
            # Fallback: look for the field text and get next element
            return ""
        except:
            return ""

    def get_page_heading(self) -> str:
        """Get page heading."""
        return self.get_element_text(self.PAGE_HEADING)

    def click_update_button(self) -> None:
        """Click update button."""
        self.click_element(self.UPDATE_BTN)
        self.wait_for_load_state("networkidle")

    def click_delete_button(self) -> None:
        """Click delete button."""
        self.click_element(self.DELETE_BTN)
        self.wait_for_load_state("networkidle")

    def click_back_button(self) -> None:
        """Click back button."""
        self.click_element(self.BACK_BTN)
        self.wait_for_load_state("networkidle")

    def is_update_button_visible(self) -> bool:
        """Check if update button is visible."""
        return self.is_element_visible(self.UPDATE_BTN)

    def is_delete_button_visible(self) -> bool:
        """Check if delete button is visible."""
        return self.is_element_visible(self.DELETE_BTN)
