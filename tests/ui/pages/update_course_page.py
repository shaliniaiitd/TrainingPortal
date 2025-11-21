"""
Update Course Page Object - represents the form for updating courses.
Extends AddCoursePage since update form is similar to add form.
"""

from .add_course_page import AddCoursePage


class UpdateCoursePage(AddCoursePage):
    """Page object for update course form page."""

    # Additional locators specific to update page
    CANCEL_BTN = "a:has-text('Cancel'), a:has-text('Back'), button:has-text('Cancel')"

    def goto_update_course(self, course_id: int) -> "UpdateCoursePage":
        """Navigate to update course page by course ID."""
        self.goto(f"/myapp/courses/{course_id}/update/")
        return self

    def is_update_form_loaded(self) -> bool:
        """Check if update course form is loaded with prepopulated data."""
        # Form should be loaded and have values
        return self.is_form_loaded() and self.get_course_name_value() != ""

    def verify_prepopulated_data(self, expected_data: dict) -> bool:
        """
        Verify that form is prepopulated with expected data.
        
        Args:
            expected_data: Dict with expected values
            
        Returns:
            True if all visible fields match expected data
        """
        if "course_name" in expected_data:
            if self.get_course_name_value() != expected_data["course_name"]:
                return False
        if "description" in expected_data:
            if self.get_description_value() != expected_data["description"]:
                return False
        return True

    def update_course_name(self, course_name: str) -> "UpdateCoursePage":
        """Update course name field."""
        self.clear_input(self.COURSE_NAME_INPUT)
        self.fill_course_name(course_name)
        return self

    def update_course_type(self, course_type: str) -> "UpdateCoursePage":
        """Update course type field."""
        self.fill_course_type(course_type)
        return self

    def update_faculty(self, faculty_name: str) -> "UpdateCoursePage":
        """Update faculty field."""
        self.fill_faculty(faculty_name)
        return self

    def update_description(self, description: str) -> "UpdateCoursePage":
        """Update description field."""
        self.clear_input(self.DESCRIPTION_INPUT)
        self.fill_description(description)
        return self

    def update_duration(self, duration: str) -> "UpdateCoursePage":
        """Update duration field."""
        self.clear_input(self.DURATION_INPUT)
        self.fill_duration(duration)
        return self

    def update_form(self, course_data: dict) -> "UpdateCoursePage":
        """
        Update course form with new data.
        Only updates fields that are provided in course_data dict.
        
        Args:
            course_data: Dict with fields to update
        """
        if "course_name" in course_data:
            self.update_course_name(course_data["course_name"])
        if "course_type" in course_data:
            self.update_course_type(course_data["course_type"])
        if "faculty" in course_data or "facultyname" in course_data:
            faculty = course_data.get("faculty") or course_data.get("facultyname")
            self.update_faculty(faculty)
        if "description" in course_data:
            self.update_description(course_data["description"])
        if "duration" in course_data:
            self.update_duration(course_data["duration"])
        return self

    def submit_update(self) -> None:
        """Submit the update form."""
        self.submit_form()
