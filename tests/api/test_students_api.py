"""Students API Tests.

Tests CRUD operations on /api/students/ endpoint.
Inherits from BaseApiTestClass and uses data models from api_models.
"""

import pytest
from tests.api.base_api_test import BaseApiTestClass
from tests.api.api_models import (
    StudentRequest, StudentResponse, ApiValidator
)


class TestStudentsAPI(BaseApiTestClass):
    """API tests for Students endpoint."""

    STUDENTS_ENDPOINT = "students"

    def test_list_students(self):
        """Test: GET /api/students/ returns student list."""
        response = self.get(self.STUDENTS_ENDPOINT)

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_key("results")
         .assert_is_list("results"))

        # Validate each student
        for student_data in response.body["results"]:
            validated = ApiValidator.validate_student_response(student_data)
            assert validated.id > 0
            ApiValidator.assert_field_not_empty(validated, "name")

    def test_create_student(self):
        """Test: POST /api/students/ creates a new student."""
        payload = StudentRequest(
            name="API Test Student",
            course_id=1,  # Assume course id=1 exists
            email="api_test@example.com",
            skills="Python, Django, Testing"
        ).to_dict()

        response = self.post(self.STUDENTS_ENDPOINT, payload)

        (self.validate(response)
         .assert_status_code(201)
         .assert_has_keys(["id", "name", "course_id"]))

        created = ApiValidator.validate_student_response(response.body)
        assert created.name == "API Test Student"
        assert created.course_id == 1

        self.created_student_id = created.id

    def test_get_student_detail(self):
        """Test: GET /api/students/{id}/ returns student detail."""
        student_id = 1
        response = self.get(f"{self.STUDENTS_ENDPOINT}/{student_id}")

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_keys(["id", "name", "course_id"]))

        student = ApiValidator.validate_student_response(response.body)
        assert student.id == student_id

    def test_update_student(self):
        """Test: PUT /api/students/{id}/ updates student."""
        student_id = 1
        update_payload = StudentRequest(
            name="Updated Student Name",
            course_id=1,
            email="updated@example.com",
            skills="Updated, Skills, List"
        ).to_dict()

        response = self.put(f"{self.STUDENTS_ENDPOINT}/{student_id}", update_payload)

        (self.validate(response)
         .assert_status_2xx()
         .assert_key_equals("name", "Updated Student Name"))

        updated = ApiValidator.validate_student_response(response.body)
        assert updated.name == "Updated Student Name"

    def test_partial_update_student(self):
        """Test: PATCH /api/students/{id}/ partially updates student."""
        student_id = 1
        partial_payload = {
            "email": "partial_update@example.com"
        }

        response = self.patch(f"{self.STUDENTS_ENDPOINT}/{student_id}", partial_payload)

        (self.validate(response)
         .assert_status_2xx()
         .assert_key_equals("email", "partial_update@example.com"))

    def test_delete_student(self):
        """Test: DELETE /api/students/{id}/ deletes student."""
        # Create a student, then delete it
        create_payload = StudentRequest(
            name="ToDeleteStudent",
            course_id=1
        ).to_dict()

        create_resp = self.post(self.STUDENTS_ENDPOINT, create_payload)
        created = ApiValidator.validate_student_response(create_resp.body)
        student_id = created.id

        # Delete it
        delete_resp = self.delete(f"{self.STUDENTS_ENDPOINT}/{student_id}")
        self.validate(delete_resp).assert_status_code(204)

    def test_create_student_with_invalid_course(self):
        """Test: POST with invalid course returns error."""
        invalid_payload = StudentRequest(
            name="Invalid Student",
            course_id=999999  # Non-existent
        ).to_dict()

        response = self.post(self.STUDENTS_ENDPOINT, invalid_payload)

        # Expect validation error
        assert response.status_code in [400, 404, 422], \
            f"Expected error for invalid course, got {response.status_code}"

    def test_get_nonexistent_student(self):
        """Test: GET non-existent student returns 404."""
        response = self.get(f"{self.STUDENTS_ENDPOINT}/999999")
        self.validate(response).assert_status_code(404)

    def test_student_with_resume_url(self):
        """Test: Student can have resume_url field."""
        payload = StudentRequest(
            name="Student With Resume",
            course_id=1,
            resume_url="https://example.com/resume.pdf"
        ).to_dict()

        response = self.post(self.STUDENTS_ENDPOINT, payload)
        self.validate(response).assert_status_code(201)

        created = ApiValidator.validate_student_response(response.body)
        assert created.resume_url == "https://example.com/resume.pdf"

    def test_list_students_pagination(self):
        """Test: Student list supports pagination."""
        response = self.get(self.STUDENTS_ENDPOINT, params={"limit": 10, "offset": 0})

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_key("count")
         .assert_has_key("results"))

        # Validate paginated response structure
        ApiValidator.validate_pagination_response(response.body)
