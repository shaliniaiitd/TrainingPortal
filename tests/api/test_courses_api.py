"""Courses API Tests.

Tests CRUD operations on /api/courses/ endpoint.
Inherits from BaseApiTestClass and uses data models from api_models.
"""

import pytest
from tests.api.base_api_test import BaseApiTestClass
from tests.api.api_models import (
    CourseRequest, CourseResponse, CourseCategory, ApiValidator
)


class TestCoursesAPI(BaseApiTestClass):
    """API tests for Courses endpoint."""

    COURSES_ENDPOINT = "courses"

    def test_list_courses(self):
        """Test: GET /api/courses/ returns course list."""
        response = self.get(self.COURSES_ENDPOINT)

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_key("results")
         .assert_is_list("results"))

        # Validate each course
        for course_data in response.body["results"]:
            validated = ApiValidator.validate_course_response(course_data)
            assert validated.id > 0
            ApiValidator.assert_field_not_empty(validated, "course_name")

    def test_create_course(self):
        """Test: POST /api/courses/ creates a new course."""
        payload = CourseRequest(
            course_name="API Test Course",
            facultyname_id=1,  # Assume faculty id=1 exists
            category=CourseCategory.PROGRAMMING.value,
            description="Test course via API"
        ).to_dict()

        response = self.post(self.COURSES_ENDPOINT, payload)

        (self.validate(response)
         .assert_status_code(201)
         .assert_has_keys(["id", "course_name", "facultyname_id"]))

        created = ApiValidator.validate_course_response(response.body)
        assert created.course_name == "API Test Course"
        assert created.facultyname_id == 1

        self.created_course_id = created.id

    def test_get_course_detail(self):
        """Test: GET /api/courses/{id}/ returns course detail."""
        course_id = 1
        response = self.get(f"{self.COURSES_ENDPOINT}/{course_id}")

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_keys(["id", "course_name", "facultyname_id"]))

        course = ApiValidator.validate_course_response(response.body)
        assert course.id == course_id

    def test_update_course(self):
        """Test: PUT /api/courses/{id}/ updates course."""
        course_id = 1
        update_payload = CourseRequest(
            course_name="Updated Course Name",
            facultyname_id=1,
            category=CourseCategory.WEB_DEV.value,
            description="Updated description"
        ).to_dict()

        response = self.put(f"{self.COURSES_ENDPOINT}/{course_id}", update_payload)

        (self.validate(response)
         .assert_status_2xx()
         .assert_key_equals("course_name", "Updated Course Name"))

        updated = ApiValidator.validate_course_response(response.body)
        assert updated.course_name == "Updated Course Name"
        assert updated.category == CourseCategory.WEB_DEV.value

    def test_partial_update_course(self):
        """Test: PATCH /api/courses/{id}/ partially updates course."""
        course_id = 1
        partial_payload = {
            "category": CourseCategory.DATA_ANALYSIS.value
        }

        response = self.patch(f"{self.COURSES_ENDPOINT}/{course_id}", partial_payload)

        (self.validate(response)
         .assert_status_2xx()
         .assert_key_equals("category", CourseCategory.DATA_ANALYSIS.value))

    def test_delete_course(self):
        """Test: DELETE /api/courses/{id}/ deletes course."""
        # Create a course, then delete it
        create_payload = CourseRequest(
            course_name="ToDeleteCourse",
            facultyname_id=1,
            category=CourseCategory.TESTING.value
        ).to_dict()

        create_resp = self.post(self.COURSES_ENDPOINT, create_payload)
        created = ApiValidator.validate_course_response(create_resp.body)
        course_id = created.id

        # Delete it
        delete_resp = self.delete(f"{self.COURSES_ENDPOINT}/{course_id}")
        self.validate(delete_resp).assert_status_code(204)

    def test_create_course_with_invalid_faculty(self):
        """Test: POST with invalid faculty returns error."""
        invalid_payload = CourseRequest(
            course_name="Invalid Course",
            facultyname_id=999999,  # Non-existent
            category=CourseCategory.PROGRAMMING.value
        ).to_dict()

        response = self.post(self.COURSES_ENDPOINT, invalid_payload)

        # Expect validation error
        assert response.status_code in [400, 404, 422], \
            f"Expected error for invalid faculty, got {response.status_code}"

    def test_get_nonexistent_course(self):
        """Test: GET non-existent course returns 404."""
        response = self.get(f"{self.COURSES_ENDPOINT}/999999")
        self.validate(response).assert_status_code(404)

    def test_course_response_has_faculty_info(self):
        """Test: Course response includes nested faculty info."""
        response = self.get(f"{self.COURSES_ENDPOINT}/1")

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_key("facultyname"))

        # facultyname should be populated (or at least present)
        assert response.body.get("facultyname") is not None or \
               isinstance(response.body.get("facultyname"), dict)
