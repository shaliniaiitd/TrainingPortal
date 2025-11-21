"""
Add Course Page Object - represents the form for adding new courses.
"""

from .base_page import BasePage


class AddCoursePage(BasePage):
    """Page object for add course form page."""

    # Locators
    COURSE_NAME_INPUT = "[name='course_name'], #id_course_name"
    COURSE_TYPE_SELECT = "select[name='course_type'], select[name='type']"
    FACULTY_SELECT = "select[name='facultyname'], select[name='faculty']"
    DESCRIPTION_INPUT = "textarea[name='description'], #id_description"
    DURATION_INPUT = "[name='duration'], #id_duration"
    SUBMIT_BTN = "button[type='submit'], input[type='submit']"
    CANCEL_BTN = "a:has-text('Cancel'), button:has-text('Cancel')"
    FORM_ELEMENT = "form"
    PAGE_HEADING = "h1, h2"

    def goto_add_course(self) -> "AddCoursePage":
        """Navigate to add course page."""
        self.goto("/myapp/addcourse/")
        return self

    def is_form_loaded(self) -> bool:
        """Check if add course form is loaded."""
        return self.is_element_visible(self.FORM_ELEMENT)

    def fill_course_name(self, course_name: str) -> "AddCoursePage":
        """Fill course name field."""
        self.fill_input(self.COURSE_NAME_INPUT, course_name)
        return self

    def fill_course_type(self, course_type: str) -> "AddCoursePage":
        """Select course type from dropdown."""
        self.select_option_by_text(self.COURSE_TYPE_SELECT, course_type)
        return self

    def fill_faculty(self, faculty_name: str) -> "AddCoursePage":
        """Select faculty from dropdown."""
        self.select_option_by_text(self.FACULTY_SELECT, faculty_name)
        return self

    def fill_description(self, description: str) -> "AddCoursePage":
        """Fill description field."""
        self.fill_input(self.DESCRIPTION_INPUT, description)
        return self

    def fill_duration(self, duration: str) -> "AddCoursePage":
        """Fill duration field."""
        self.fill_input(self.DURATION_INPUT, duration)
        return self

    def fill_form(self, course_data: dict) -> "AddCoursePage":
        """
        Fill entire course form with data dict.
        
        Args:
            course_data: Dict with keys: course_name, course_type, faculty, description, duration
        """
        if "course_name" in course_data:
            self.fill_course_name(course_data["course_name"])
        if "course_type" in course_data:
            self.fill_course_type(course_data["course_type"])
        if "faculty" in course_data or "facultyname" in course_data:
            faculty = course_data.get("faculty") or course_data.get("facultyname")
            self.fill_faculty(faculty)
        if "description" in course_data:
            self.fill_description(course_data["description"])
        if "duration" in course_data:
            self.fill_duration(course_data["duration"])
        return self

    def submit_form(self) -> None:
        """Submit the form."""
        self.click_element(self.SUBMIT_BTN)
        self.wait_for_load_state("networkidle")

    def cancel_form(self) -> None:
        """Cancel form and go back."""
        self.click_element(self.CANCEL_BTN)
        self.wait_for_load_state("networkidle")

    def get_course_name_value(self) -> str:
        """Get current course name value."""
        return self.get_input_value(self.COURSE_NAME_INPUT)

    def get_course_type_value(self) -> str:
        """Get current course type value."""
        return self.get_input_value(self.COURSE_TYPE_SELECT)

    def get_faculty_value(self) -> str:
        """Get current faculty value."""
        return self.get_input_value(self.FACULTY_SELECT)

    def get_description_value(self) -> str:
        """Get current description value."""
        return self.get_input_value(self.DESCRIPTION_INPUT)

    def get_duration_value(self) -> str:
        """Get current duration value."""
        return self.get_input_value(self.DURATION_INPUT)

    def is_course_name_visible(self) -> bool:
        """Check if course name field is visible."""
        return self.is_element_visible(self.COURSE_NAME_INPUT)

    def is_course_type_visible(self) -> bool:
        """Check if course type field is visible."""
        return self.is_element_visible(self.COURSE_TYPE_SELECT)

    def is_faculty_visible(self) -> bool:
        """Check if faculty field is visible."""
        return self.is_element_visible(self.FACULTY_SELECT)

    def is_submit_button_visible(self) -> bool:
        """Check if submit button is visible."""
        return self.is_element_visible(self.SUBMIT_BTN)

    def get_page_heading(self) -> str:
        """Get page heading."""
        return self.get_element_text(self.PAGE_HEADING)
