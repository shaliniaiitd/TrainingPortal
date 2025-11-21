"""Members API Tests.

Tests CRUD operations on /api/members/ endpoint.
Inherits from BaseApiTestClass and uses data models from api_models.
Demonstrates request/response validation and fluent validator chains.
"""

import pytest
from tests.api.base_api_test import BaseApiTestClass
from tests.api.api_models import (
    MemberRequest, MemberResponse, ApiValidator,
    HttpMethod
)


class TestMembersAPI(BaseApiTestClass):
    """API tests for Members endpoint."""

    MEMBERS_ENDPOINT = "members"

    def test_list_members(self):
        """Test: GET /api/members/ returns member list."""
        response = self.get(self.MEMBERS_ENDPOINT)

        # Fluent validation chain
        (self.validate(response)
         .assert_status_2xx()
         .assert_has_key("results")
         .assert_is_list("results"))

        # Validate each member in results has required fields
        for member_data in response.body["results"]:
            validated = ApiValidator.validate_member_response(member_data)
            assert validated.id > 0
            ApiValidator.assert_field_not_empty(validated, "firstname")
            ApiValidator.assert_field_not_empty(validated, "lastname")

    def test_create_member(self):
        """Test: POST /api/members/ creates a new member."""
        payload = MemberRequest(
            first_name="API_Test",
            last_name="Member",
            designation="Test Trainer"
        ).to_dict()

        response = self.post(self.MEMBERS_ENDPOINT, payload)

        # Validate response
        (self.validate(response)
         .assert_status_code(201)  # Created
         .assert_has_keys(["id", "first_name", "last_name", "designation"]))

        # Parse and validate response data
        created = ApiValidator.validate_member_response(response.body)
        assert created.first_name == "API_Test"
        assert created.last_name == "Member"
        assert created.designation == "Test Trainer"

        # Store id for later tests
        self.created_member_id = created.id

    def test_get_member_detail(self):
        """Test: GET /api/members/{id}/ returns member detail."""
        # Use first member (id=1) for test
        member_id = 1
        response = self.get(f"{self.MEMBERS_ENDPOINT}/{member_id}")

        (self.validate(response)
         .assert_status_2xx()
         .assert_has_keys(["id", "first_name", "last_name"]))

        member = ApiValidator.validate_member_response(response.body)
        assert member.id == member_id

    def test_update_member(self):
        """Test: PUT /api/members/{id}/ updates member."""
        member_id = 1
        update_payload = MemberRequest(
            first_name="UpdatedName",
            last_name="UpdatedLast",
            designation="Updated Role"
        ).to_dict()

        response = self.put(f"{self.MEMBERS_ENDPOINT}/{member_id}", update_payload)

        (self.validate(response)
         .assert_status_2xx()
         .assert_key_equals("first_name", "UpdatedName"))

        updated = ApiValidator.validate_member_response(response.body)
        assert updated.first_name == "UpdatedName"

    def test_partial_update_member(self):
        """Test: PATCH /api/members/{id}/ partially updates member."""
        member_id = 1
        partial_payload = {"designation": "Partial Update Designation"}

        response = self.patch(f"{self.MEMBERS_ENDPOINT}/{member_id}", partial_payload)

        (self.validate(response)
         .assert_status_2xx()
         .assert_key_equals("designation", "Partial Update Designation"))

    def test_delete_member(self):
        """Test: DELETE /api/members/{id}/ deletes member."""
        # Create a member first, then delete it
        create_payload = MemberRequest(
            first_name="ToDelete",
            last_name="Member",
            designation="Temp"
        ).to_dict()

        create_resp = self.post(self.MEMBERS_ENDPOINT, create_payload)
        created = ApiValidator.validate_member_response(create_resp.body)
        member_id = created.id

        # Delete it
        delete_resp = self.delete(f"{self.MEMBERS_ENDPOINT}/{member_id}")
        self.validate(delete_resp).assert_status_code(204)  # No Content

    def test_create_member_validation_errors(self):
        """Test: POST with invalid data returns 400."""
        invalid_payload = {
            "first_name": "",  # Empty
            "last_name": "OnlyLast",
            # Missing designation
        }

        response = self.post(self.MEMBERS_ENDPOINT, invalid_payload)

        # Expect validation error (400 or 422)
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for invalid payload, got {response.status_code}"

    def test_get_nonexistent_member(self):
        """Test: GET non-existent member returns 404."""
        response = self.get(f"{self.MEMBERS_ENDPOINT}/999999")
        self.validate(response).assert_status_code(404)

    def test_delete_nonexistent_member(self):
        """Test: DELETE non-existent member returns 404."""
        response = self.delete(f"{self.MEMBERS_ENDPOINT}/999999")
        self.validate(response).assert_status_code(404)

    def test_list_members_response_time(self):
        """Test: List members response time is acceptable."""
        response = self.get(self.MEMBERS_ENDPOINT)
        # Assert response time is under 2 seconds
        self.validate(response).assert_response_time_ms(2000)
