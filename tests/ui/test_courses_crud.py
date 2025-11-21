"""Course CRUD tests using PageFactory and Page Objects.

Exercises add, update, delete course flows and demonstrates use of
page objects and builder for data-driven fill. Inherits from BaseTestClass.
"""

import pytest
from tests.ui.base_test import BaseTestClass


class TestCoursesCRUD(BaseTestClass):
    """CRUD tests for Courses — inherits from BaseTestClass."""

    def test_create_course(self):
        """Test: Create a new course."""
        courses = self.get_page("courses")
        courses.goto_courses_list()
        self.assert_page_loaded(courses, "is_courses_page_loaded")

        before = courses.get_courses_count()

        add_course = self.get_page("add_course")
        add_course.goto_add_course()
        self.assert_page_loaded(add_course, "is_form_loaded")

        # Use Builder to construct form declaratively
        form = (
            self.build_form("course")
            .add_text("course_name", "[name='course_name']", "Automated Course")
            .add_select("course_type", "select[name='course_type']", "Programming")
            .add_textarea("description", "textarea[name='description']", "Auto-generated course for tests")
            .add_text("duration", "[name='duration']", "4 weeks")
            .build()
        )

        form.fill(add_course)
        add_course.submit_form()

        courses.goto_courses_list()
        after = courses.get_courses_count()
        self.assert_count_increased(before, after, delta=1)
        assert courses.course_exists("Automated Course"), "Created course not found in list"

    def test_read_course_detail(self):
        """Test: Read course details from detail page."""
        detail = self.get_page("course_detail")
        detail.goto_course_detail(1)
        self.assert_page_loaded(detail, "is_detail_page_loaded")

        # Verify heading is present
        heading = detail.get_page_heading()
        assert heading, "Course detail page has no heading"

    def test_update_course(self):
        """Test: Update course details."""
        # Assume course id=1 exists for update test
        update = self.get_page("update_course")
        update.goto_update_course(1)
        self.assert_page_loaded(update, "is_form_loaded")

        updated_name = "Updated Course Name"
        update.fill_course_name(updated_name)
        update.submit_form()

        # Verify by checking detail page
        detail = self.get_page("course_detail")
        detail.goto_course_detail(1)
        name = detail.get_course_name()
        assert updated_name.lower() in name.lower(), f"Updated course name not found: {name}"

    def test_delete_course(self):
        """Test: Delete a course."""
        courses = self.get_page("courses")
        courses.goto_courses_list()
        before = courses.get_courses_count()

        if before == 0:
            pytest.skip("No courses available to delete")

        courses.click_delete_course(0)
        # Try to confirm deletion if dialog appears
        try:
            self.page.click("button:has-text('Confirm'), button:has-text('Yes')")
        except Exception:
            pass

        courses.goto_courses_list()
        after = courses.get_courses_count()
        self.assert_count_decreased(before, after, delta=1)
