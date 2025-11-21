"""
Courses Page Object - represents the courses list page.
"""

from .base_page import BasePage


class CoursesPage(BasePage):
    """Page object for courses list page at /myapp/courses/"""

    # Locators
    PAGE_HEADING = "h1, h2"
    ADD_COURSE_BTN = "a:has-text('Add Course'), button:has-text('Add Course')"
    COURSES_TABLE = "table"
    COURSE_ROWS = "table tbody tr"
    COURSE_NAME_CELLS = "table tbody tr td:first-child"
    DELETE_BTNS = "button:has-text('Delete'), a:has-text('Delete')"
    UPDATE_BTNS = "button:has-text('Update'), a:has-text('Update'), button:has-text('Edit')"
    COURSES_LINK = "a:has-text('Courses')"

    def goto_courses_list(self) -> "CoursesPage":
        """Navigate to courses list page."""
        self.goto("/myapp/courses/")
        return self

    def is_courses_page_loaded(self) -> bool:
        """Check if courses page is loaded."""
        return self.is_element_visible(self.COURSES_TABLE)

    def click_add_course(self) -> None:
        """Click Add Course button."""
        self.click_element(self.ADD_COURSE_BTN)
        self.wait_for_load_state("networkidle")

    def get_courses_count(self) -> int:
        """Get number of courses in table."""
        return self.get_table_row_count(self.COURSES_TABLE)

    def get_courses_names(self) -> list:
        """Get list of all course names."""
        return self.get_table_column_values(self.COURSES_TABLE, 0)

    def course_exists(self, course_name: str) -> bool:
        """Check if a course exists in the list."""
        names = self.get_courses_names()
        return any(course_name.lower() in name.lower() for name in names)

    def click_delete_course(self, course_index: int = 0) -> None:
        """Click delete button for a course."""
        delete_buttons = self.page.locator(self.DELETE_BTNS).all()
        if course_index < len(delete_buttons):
            delete_buttons[course_index].click()

    def click_update_course(self, course_index: int = 0) -> None:
        """Click update button for a course."""
        update_buttons = self.page.locator(self.UPDATE_BTNS).all()
        if course_index < len(update_buttons):
            update_buttons[course_index].click()
            self.wait_for_load_state("networkidle")

    def click_course_by_name(self, course_name: str) -> None:
        """Click on a course by name."""
        self.click_by_text(course_name)
        self.wait_for_load_state("networkidle")

    def get_page_heading(self) -> str:
        """Get page heading."""
        return self.get_element_text(self.PAGE_HEADING)

    def is_add_course_button_visible(self) -> bool:
        """Check if Add Course button is visible."""
        return self.is_element_visible(self.ADD_COURSE_BTN)

    def has_table(self) -> bool:
        """Check if courses table exists."""
        return self.element_count(self.COURSES_TABLE) > 0
