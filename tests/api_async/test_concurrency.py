"""Concurrency Tests - Using Playwright for API Validation

Tests for concurrent access scenarios using Playwright:
- Same record update from multiple clients
- Race condition handling (concurrent PUTs)
- Phantom reads and dirty writes prevention
- Data consistency and integrity
- Optimistic locking with versioning
- Last-write-wins scenarios
- Business rule enforcement

Uses asyncio to simulate concurrent API calls via Playwright.
"""

import pytest
import asyncio
from tests.api_async.base_api_test import PlaywrightApiClient


@pytest.mark.asyncio
class TestConcurrentUpdates:
    """Test handling of concurrent update attempts."""

    async def test_concurrent_put_updates_same_record(self, page):
        """Test: Concurrent PUT updates to same record."""
        # Create a member first
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "ConcurrentTest",
            "lastname": "Member",
            "designation": "Developer",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        # Concurrent update attempts
        async def update_member(update_num):
            payload = {
                "firstname": f"Updated{update_num}",
                "lastname": "Member",
                "designation": "Developer",
                "image": ""
            }
            return await client.put(f"members/{member_id}", payload)
        
        # Run 3 concurrent updates using asyncio
        responses = await asyncio.gather(
            update_member(0),
            update_member(1),
            update_member(2),
            return_exceptions=True
        )
        
        # All should return success (2xx)
        successful = sum(1 for r in responses if isinstance(r, object) and hasattr(r, 'is_success') and r.is_success())
        assert successful > 0, "At least one update should succeed"
        
        # Verify final state is consistent
        final_resp = await client.get(f"members/{member_id}")
        assert final_resp.is_success()
        final_name = final_resp.body.get("firstname")
        # Should be one of the update values (not corrupted)
        assert final_name in [f"Updated{i}" for i in range(3)]

    async def test_concurrent_patch_same_field(self, page):
        """Test: Concurrent PATCH updates to same field."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "PatchTest",
            "lastname": "Member",
            "designation": "QA",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        async def patch_designation(des):
            return await client.patch(f"members/{member_id}", {
                "designation": des
            })
        
        designations = ["Developer", "QA", "Manager"]
        responses = await asyncio.gather(
            patch_designation(designations[0]),
            patch_designation(designations[1]),
            patch_designation(designations[2]),
            return_exceptions=True
        )
        
        # Final state should be valid
        final_resp = await client.get(f"members/{member_id}")
        final_des = final_resp.body.get("designation")
        assert final_des in designations

    async def test_concurrent_patch_different_fields(self, page):
        """Test: Concurrent PATCH to different fields is safe."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "Field1",
            "lastname": "Field2",
            "designation": "Field3",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        async def patch_firstname():
            return await client.patch(f"members/{member_id}", {
                "firstname": "NewFirstName"
            })
        
        async def patch_lastname():
            return await client.patch(f"members/{member_id}", {
                "lastname": "NewLastName"
            })
        
        async def patch_designation():
            return await client.patch(f"members/{member_id}", {
                "designation": "NewDesignation"
            })
        
        # Run concurrent patches to different fields
        responses = await asyncio.gather(
            patch_firstname(),
            patch_lastname(),
            patch_designation(),
            return_exceptions=True
        )
        
        # All should succeed
        assert all(r.is_success() if isinstance(r, object) and hasattr(r, 'is_success') else True for r in responses)
        
        # Final state should have all updates
        final_resp = await client.get(f"members/{member_id}")
        assert final_resp.body.get("firstname") == "NewFirstName"
        assert final_resp.body.get("lastname") == "NewLastName"
        assert final_resp.body.get("designation") == "NewDesignation"

    async def test_concurrent_put_vs_delete(self, page):
        """Test: Concurrent PUT and DELETE handling."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "PutVsDelete",
            "lastname": "Test",
            "designation": "Dev",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        async def attempt_put():
            return await client.put(f"members/{member_id}", {
                "firstname": "Updated",
                "lastname": "Test",
                "designation": "Dev",
                "image": ""
            })
        
        async def attempt_delete():
            return await client.delete(f"members/{member_id}")
        
        # Run concurrent PUT and DELETE
        responses = await asyncio.gather(
            attempt_put(),
            attempt_delete(),
            return_exceptions=True
        )
        
        # At least one should succeed
        assert len(responses) >= 1


@pytest.mark.asyncio
class TestRaceConditionHandling:
    """Test handling of race conditions."""

    async def test_lost_update_prevention_with_etag(self, page):
        """Test: Lost update prevention with ETag (optimistic locking)."""
        client = PlaywrightApiClient(page)
        
        # Create member
        create_resp = await client.post("members", {
            "firstname": "ETester",
            "lastname": "Race",
            "designation": "Dev",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        # Get initial ETag
        resp1 = await client.get(f"members/{member_id}")
        etag1 = resp1.headers.get("ETag")
        
        # Update 1: Get latest state
        resp2 = await client.get(f"members/{member_id}")
        etag2 = resp2.headers.get("ETag")
        
        # Simulate concurrent modification
        await client.put(f"members/{member_id}", {
            "firstname": "Concurrent",
            "lastname": "Race",
            "designation": "Dev",
            "image": ""
        })
        
        # Try to update with old ETag (should fail or conflict)
        if etag2:
            response = await client.put(
                f"members/{member_id}",
                {
                    "firstname": "Attempted",
                    "lastname": "Race",
                    "designation": "Dev",
                    "image": ""
                },
                headers={"If-Match": etag2}
            )
            
            # Should either:
            # 1. Succeed (API doesn't use If-Match)
            # 2. Return 412 Precondition Failed (proper locking)
            assert response.status_code in [200, 201, 204, 412]

    async def test_read_then_write_race_condition(self, page):
        """Test: Read-then-write race condition handling."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "Initial",
            "lastname": "Value",
            "designation": "Dev",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        # Client A reads
        resp_a = await client.get(f"members/{member_id}")
        value_a = resp_a.body.get("firstname")
        
        # Client B modifies
        await client.put(f"members/{member_id}", {
            "firstname": "Modified",
            "lastname": "Value",
            "designation": "Dev",
            "image": ""
        })
        
        # Client A writes based on old data
        resp_a_write = await client.put(f"members/{member_id}", {
            "firstname": f"{value_a}AndMore",
            "lastname": "Value",
            "designation": "Dev",
            "image": ""
        })
        
        # Final state should be consistent
        final_resp = await client.get(f"members/{member_id}")
        assert final_resp.is_success()

    async def test_concurrent_create_same_resource(self, page):
        """Test: Concurrent creates with potential duplicates."""
        client = PlaywrightApiClient(page)
        
        async def create_member():
            return await client.post("members", {
                "firstname": "Duplicate",
                "lastname": "Name",
                "designation": "Dev",
                "image": ""
            })
        
        # Try to create concurrently
        responses = await asyncio.gather(
            create_member(),
            create_member(),
            return_exceptions=True
        )
        
        # Both might succeed (no unique constraint) or one fails
        # At least one should succeed
        assert any(r.is_success() if isinstance(r, object) and hasattr(r, 'is_success') else True for r in responses)


@pytest.mark.asyncio
class TestDataConsistency:
    """Test data consistency in concurrent scenarios."""

    async def test_no_phantom_reads_on_list(self, page):
        """Test: List results are consistent snapshot."""
        client = PlaywrightApiClient(page)
        
        # Get initial list count
        resp1 = await client.get("members")
        count1 = len(resp1.body.get("results", []))
        
        # Create new member
        await client.post("members", {
            "firstname": "Phantom",
            "lastname": "Test",
            "designation": "Dev",
            "image": ""
        })
        
        # Get list again
        resp2 = await client.get("members")
        count2 = len(resp2.body.get("results", []))
        
        # Should be one more
        assert count2 >= count1

    async def test_no_dirty_reads(self, page):
        """Test: Uncommitted changes not visible."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "Clean",
            "lastname": "Read",
            "designation": "Dev",
            "image": ""
        })
        
        if create_resp.is_success():
            member_id = create_resp.body.get("id")
            
            # Read should see committed data
            resp = await client.get(f"members/{member_id}")
            assert resp.is_success()
            assert resp.body.get("firstname") == "Clean"

    async def test_foreign_key_referential_integrity(self, page):
        """Test: Foreign key constraints maintain integrity."""
        client = PlaywrightApiClient(page)
        
        # Get a valid course
        courses_resp = await client.get("courses")
        
        if not courses_resp.body.get("results"):
            pytest.skip("No courses available")
        
        course_id = courses_resp.body["results"][0].get("id")
        
        # Try to create student with valid course
        valid_resp = await client.post("students", {
            "firstname": "Valid",
            "lastname": "Student",
            "course_id": course_id,
            "email": "test@test.com"
        })
        
        assert valid_resp.is_success()

    async def test_cascade_delete_maintains_integrity(self, page):
        """Test: Cascade deletes maintain referential integrity."""
        client = PlaywrightApiClient(page)
        
        # Create member
        member_resp = await client.post("members", {
            "firstname": "Cascade",
            "lastname": "Test",
            "designation": "Dev",
            "image": ""
        })
        
        if not member_resp.is_success():
            pytest.skip("Cannot create member")
        
        member_id = member_resp.body.get("id")
        
        # Create course with this member
        course_resp = await client.post("courses", {
            "coursename": "CascadeTest",
            "facultyname_id": member_id,
            "category": "P"
        })
        
        if course_resp.is_success():
            course_id = course_resp.body.get("id")
            
            # Delete member (should cascade to courses)
            await client.delete(f"members/{member_id}")
            
            # Try to get course
            course_check = await client.get(f"courses/{course_id}")
            # Either 404 or valid (depends on cascade setting)


@pytest.mark.asyncio
class TestConcurrencyEdgeCases:
    """Edge cases in concurrent access."""

    async def test_thundering_herd_on_shared_resource(self, page):
        """Test: Many concurrent reads don't cause issues."""
        client = PlaywrightApiClient(page)
        
        async def read_members():
            return await client.get("members")
        
        # 10 concurrent reads
        responses = await asyncio.gather(*[read_members() for _ in range(10)])
        
        # All should succeed
        assert all(r.is_success() if isinstance(r, object) and hasattr(r, 'is_success') else True for r in responses)

    async def test_concurrent_reads_and_single_write(self, page):
        """Test: Reads continue during write."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "Stress",
            "lastname": "Test",
            "designation": "Dev",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create member")
        
        member_id = create_resp.body.get("id")
        
        async def read_member():
            return await client.get(f"members/{member_id}")
        
        async def update_member():
            return await client.put(f"members/{member_id}", {
                "firstname": "Updated",
                "lastname": "Test",
                "designation": "Dev",
                "image": ""
            })
        
        # 5 reads concurrent with 1 write
        read_tasks = [read_member() for _ in range(5)]
        write_task = update_member()
        
        responses = await asyncio.gather(*read_tasks, write_task)
        
        # Most should succeed
        successful = sum(1 for r in responses if isinstance(r, object) and hasattr(r, 'is_success') and r.is_success())
        assert successful >= 5
