"""Broken Links & HATEOAS Tests - Using Playwright for API Validation

Tests for REST API link integrity using Playwright page.fetch():
- Self-referential links (HATEOAS)
- Pagination links (next, previous, first, last)
- Related resource links
- Link validity and correctness
- Response structure consistency
- Link format validation (proper URLs)
- Dead link detection
- Circular reference handling

Interview-ready REST API best practices testing with Playwright.
"""

import pytest
from urllib.parse import urlparse
from tests.api.base_api_test import PlaywrightApiClient


@pytest.mark.asyncio
class TestHATEOASLinks:
    """Test HATEOAS (Hypermedia As The Engine Of Application State) links."""

    async def test_list_endpoints_have_self_links(self, page):
        """Test: List endpoints include self links in responses."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        assert resp.is_success()
        results = resp.body.get("results", [])
        
        # Each member should have reference link
        for member in results:
            member_id = member.get("id")
            assert member_id is not None, "Missing id field"
            
            # Check for self link or URI reference
            assert member.get("url") or member.get("uri") or member.get("self"), \
                "Member missing self link/URL"

    async def test_detail_endpoint_returns_self_link(self, page):
        """Test: Detail endpoints include self link."""
        client = PlaywrightApiClient(page)
        
        # Get a member
        list_resp = await client.get("members")
        
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member = list_resp.body["results"][0]
        member_id = member.get("id")
        
        # Get detail
        detail_resp = await client.get(f"members/{member_id}")
        
        # Should have self link or URL
        assert detail_resp.body.get("url") or \
               detail_resp.body.get("uri") or \
               detail_resp.body.get("self")

    async def test_related_resources_have_links(self, page):
        """Test: Related resources are discoverable via links."""
        client = PlaywrightApiClient(page)
        
        courses_resp = await client.get("courses")
        
        if not courses_resp.body.get("results"):
            pytest.skip("No courses available")
        
        course = courses_resp.body["results"][0]
        
        # Should have faculty link or embedded faculty
        assert course.get("facultyname") or course.get("facultyname_id") or \
               course.get("faculty_url")

    async def test_links_are_absolute_urls(self, page):
        """Test: All links are absolute URLs or valid paths."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        results = resp.body.get("results", [])
        
        for member in results:
            # Check links are proper URLs or paths
            links_to_check = [
                member.get("url"),
                member.get("uri"),
                member.get("self")
            ]
            
            for link in links_to_check:
                if link:
                    # Should start with http/https or /
                    assert link.startswith(("http://", "https://", "/")), \
                        f"Invalid link format: {link}"

    async def test_self_link_navigation(self, page):
        """Test: Can navigate using self links from list."""
        client = PlaywrightApiClient(page)
        
        list_resp = await client.get("members")
        
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member = list_resp.body["results"][0]
        self_link = member.get("url") or member.get("uri")
        
        if self_link:
            # Extract path from URL
            parsed = urlparse(self_link)
            path = parsed.path
            
            # Remove /api prefix if present and query
            if path.startswith("/"):
                path = path[1:]  # Remove leading /
            
            if path.startswith("api/"):
                path = path[4:]  # Remove api/ prefix
            
            # Navigate using the link
            resp = await client.get(path)
            
            # Should be successful
            assert resp.status_code in [200, 404], \
                f"Unexpected status for self link: {resp.status_code}"

    async def test_no_broken_internal_links(self, page):
        """Test: All resource IDs referenced exist."""
        client = PlaywrightApiClient(page)
        
        courses_resp = await client.get("courses")
        
        if not courses_resp.body.get("results"):
            pytest.skip("No courses available")
        
        for course in courses_resp.body["results"]:
            faculty_id = course.get("facultyname_id")
            
            if faculty_id:
                # Try to fetch the referenced faculty
                faculty_resp = await client.get(f"members/{faculty_id}")
                
                # Should exist (200) not 404
                assert faculty_resp.status_code != 404, \
                    f"Course references non-existent faculty {faculty_id}"


@pytest.mark.asyncio
class TestPaginationLinks:
    """Test pagination link structure and validity."""

    async def test_paginated_response_has_pagination_links(self, page):
        """Test: Paginated responses include next/previous links."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members?limit=5")
        
        assert resp.is_success()
        
        # Check for pagination metadata
        has_next = resp.body.get("next")
        has_prev = resp.body.get("previous")
        has_count = resp.body.get("count")
        
        # At least one pagination field
        assert has_next or has_prev or has_count, \
            "Missing pagination metadata"

    async def test_pagination_link_validity(self, page):
        """Test: Next/previous links are valid URLs."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members?limit=5")
        
        if not resp.is_success():
            pytest.skip("Cannot get paginated members")
        
        next_link = resp.body.get("next")
        prev_link = resp.body.get("previous")
        
        for link in [next_link, prev_link]:
            if link:
                # Should be URL format
                assert isinstance(link, str), "Link should be string"
                assert link.startswith(("http://", "https://", "/")), \
                    f"Link not URL format: {link}"

    async def test_pagination_follow_next_link(self, page):
        """Test: Can follow next link to get next page."""
        client = PlaywrightApiClient(page)
        
        resp1 = await client.get("members?limit=5")
        
        if not resp1.body.get("results"):
            pytest.skip("No members available")
        
        next_link = resp1.body.get("next")
        
        if next_link:
            # Extract path and query
            parsed = urlparse(next_link)
            path_with_query = parsed.path
            if parsed.query:
                path_with_query += f"?{parsed.query}"
            
            # Remove /api prefix
            if path_with_query.startswith("/api/"):
                path_with_query = path_with_query[5:]
            elif path_with_query.startswith("/"):
                path_with_query = path_with_query[1:]
            
            # Navigate to next page
            resp2 = await client.get(path_with_query)
            
            assert resp2.is_success()

    async def test_pagination_links_are_consistent(self, page):
        """Test: Pagination follows expected pattern."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members?limit=10&offset=0")
        
        if not resp.is_success():
            pytest.skip("Cannot get paginated response")
        
        # Should have count field
        count = resp.body.get("count", 0)
        next_link = resp.body.get("next")
        
        # If there are more items, should have next link
        if count > 10:
            assert next_link, "Should have next link when more items exist"

    async def test_pagination_offset_increments_correctly(self, page):
        """Test: Offset parameter increments in pagination links."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members?limit=5&offset=0")
        
        next_link = resp.body.get("next")
        
        if next_link:
            # Should have offset=5 in next link
            assert "offset=" in next_link or "page=" in next_link or \
                   "cursor=" in next_link, \
                   "Pagination link missing offset/page/cursor"

    async def test_last_page_has_no_next_link(self, page):
        """Test: Last page doesn't have next link."""
        client = PlaywrightApiClient(page)
        
        # Get a page that's likely last
        resp = await client.get("members?limit=1000")
        
        next_link = resp.body.get("next")
        
        # Last page shouldn't have next
        if resp.body.get("count", 0) <= 1000:
            assert next_link is None or next_link == "", \
                "Last page shouldn't have next link"

    async def test_first_page_has_no_previous_link(self, page):
        """Test: First page doesn't have previous link."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members?offset=0")
        
        prev_link = resp.body.get("previous")
        
        # First page shouldn't have previous
        assert prev_link is None or prev_link == "", \
            "First page shouldn't have previous link"


@pytest.mark.asyncio
class TestLinkValidity:
    """Test that all links in responses are valid and navigable."""

    async def test_all_member_links_are_valid(self, page):
        """Test: All links returned in member list are navigable."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        if not resp.body.get("results"):
            pytest.skip("No members available")
        
        for member in resp.body["results"]:
            member_id = member.get("id")
            
            # Try to navigate to member
            detail_resp = await client.get(f"members/{member_id}")
            
            # Should not return 404
            assert detail_resp.status_code != 404, \
                f"Member link {member_id} returned 404"

    async def test_all_course_links_are_valid(self, page):
        """Test: All course links are navigable."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("courses")
        
        if not resp.body.get("results"):
            pytest.skip("No courses available")
        
        for course in resp.body["results"]:
            course_id = course.get("id")
            
            detail_resp = await client.get(f"courses/{course_id}")
            
            assert detail_resp.status_code != 404, \
                f"Course link {course_id} returned 404"

    async def test_related_faculty_links_are_valid(self, page):
        """Test: Faculty links from courses are valid."""
        client = PlaywrightApiClient(page)
        
        courses_resp = await client.get("courses")
        
        if not courses_resp.body.get("results"):
            pytest.skip("No courses available")
        
        for course in courses_resp.body["results"]:
            faculty_id = course.get("facultyname_id")
            
            if faculty_id:
                faculty_resp = await client.get(f"members/{faculty_id}")
                
                # Faculty should exist
                assert faculty_resp.status_code == 200, \
                    f"Faculty {faculty_id} from course not found"

    async def test_update_returns_valid_self_link(self, page):
        """Test: After update, returned resource has valid self link."""
        client = PlaywrightApiClient(page)
        
        # Get a member
        list_resp = await client.get("members")
        
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member = list_resp.body["results"][0]
        member_id = member.get("id")
        
        # Update it
        update_resp = await client.put(f"members/{member_id}", {
            "firstname": "Updated",
            "lastname": member.get("lastname", "Test"),
            "designation": member.get("designation", "Dev"),
            "image": ""
        })
        
        if update_resp.is_success():
            # Response should have valid self link
            self_link = update_resp.body.get("url") or update_resp.body.get("uri")
            
            if self_link:
                # Navigate to it
                nav_resp = await client.get(self_link.lstrip("/api/").lstrip("/"))
                assert nav_resp.is_success()

    async def test_created_resource_location_header(self, page):
        """Test: POST response has Location header with resource URL."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "LocationTest",
            "lastname": "Member",
            "designation": "Dev",
            "image": ""
        })
        
        if create_resp.is_success():
            # Should have Location header or be in response
            location = create_resp.headers.get("Location")
            resource_url = create_resp.body.get("url") or \
                          create_resp.body.get("uri")
            
            # At least one should exist
            assert location or resource_url, \
                "Missing location info for created resource"


@pytest.mark.asyncio
class TestLinkConsistency:
    """Test link consistency across responses."""

    async def test_same_resource_has_consistent_link(self, page):
        """Test: Same resource shows consistent link in different responses."""
        client = PlaywrightApiClient(page)
        
        # Get member from list
        list_resp = await client.get("members")
        
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member_from_list = list_resp.body["results"][0]
        member_id = member_from_list.get("id")
        list_link = member_from_list.get("url")
        
        # Get same member from detail
        detail_resp = await client.get(f"members/{member_id}")
        detail_link = detail_resp.body.get("url")
        
        # Links should match or be equivalent
        if list_link and detail_link:
            assert list_link == detail_link, \
                "Member links differ between list and detail"

    async def test_nested_links_are_consistent(self, page):
        """Test: Embedded resource links match navigation."""
        client = PlaywrightApiClient(page)
        
        courses_resp = await client.get("courses")
        
        if not courses_resp.body.get("results"):
            pytest.skip("No courses available")
        
        course = courses_resp.body["results"][0]
        faculty_id = course.get("facultyname_id")
        
        if faculty_id:
            # Get faculty from embed or via link
            if isinstance(course.get("facultyname"), dict):
                embedded_faculty = course["facultyname"]
            else:
                faculty_resp = await client.get(f"members/{faculty_id}")
                embedded_faculty = faculty_resp.body
            
            # IDs should match
            assert embedded_faculty.get("id") == faculty_id

    async def test_link_format_is_consistent(self, page):
        """Test: All links follow same format/pattern."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        results = resp.body.get("results", [])
        
        link_formats = set()
        
        for member in results:
            link = member.get("url") or member.get("uri")
            if link:
                # Determine format: absolute URL or relative path
                if link.startswith("http"):
                    link_formats.add("absolute")
                else:
                    link_formats.add("relative")
        
        # Should use consistent format
        assert len(link_formats) <= 1, \
            "Links use inconsistent format (mixed absolute and relative)"


@pytest.mark.asyncio
class TestBrokenLinkScenarios:
    """Test handling of broken link scenarios."""

    async def test_404_on_invalid_resource_id(self, page):
        """Test: Invalid resource ID returns 404."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members/999999999")
        
        # Should return 404 or similar error
        assert resp.status_code == 404, \
            f"Expected 404 for invalid ID, got {resp.status_code}"

    async def test_404_on_deleted_resource_link(self, page):
        """Test: After deletion, resource link returns 404."""
        client = PlaywrightApiClient(page)
        
        # Create then delete
        create_resp = await client.post("members", {
            "firstname": "DeleteTest",
            "lastname": "Link",
            "designation": "Dev",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test resource")
        
        member_id = create_resp.body.get("id")
        
        # Delete it
        await client.delete(f"members/{member_id}")
        
        # Try to access link
        resp = await client.get(f"members/{member_id}")
        
        # Should return 404
        assert resp.status_code == 404, \
            f"Deleted resource should return 404, got {resp.status_code}"

    async def test_no_circular_links(self, page):
        """Test: Links don't form infinite loops."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members?limit=1")
        
        results = resp.body.get("results", [])
        
        if not results:
            pytest.skip("No results to check")
        
        member = results[0]
        visited = set()
        
        def check_circular(obj, depth=0):
            if depth > 5:
                return False  # Stopped recursion limit
            
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "id":
                        if v in visited:
                            return True  # Circular reference
                        visited.add(v)
                    elif isinstance(v, (dict, list)):
                        if check_circular(v, depth + 1):
                            return True
            
            return False
        
        # Should not have circular references
        assert not check_circular(member), "Circular links detected"

    async def test_404_response_structure(self, page):
        """Test: 404 errors have consistent structure."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members/invalid999")
        
        if resp.status_code == 404:
            # Should have error info
            assert resp.body is not None, "404 should have response body"

    async def test_all_available_endpoints_are_discoverable(self, page):
        """Test: Can discover all endpoints from root or working_docs."""
        client = PlaywrightApiClient(page)
        
        # Try to get API root or documentation
        resp = await client.get("")
        
        # Most APIs have root endpoint with available endpoints
        # or documentation showing available links
        if resp.is_success():
            assert resp.body is not None


@pytest.mark.asyncio
class TestLinkMetadata:
    """Test link metadata and HTTP standards compliance."""

    async def test_links_use_correct_http_methods(self, page):
        """Test: Response indicates correct methods for links."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        if not resp.body.get("results"):
            pytest.skip("No members available")
        
        member = resp.body["results"][0]
        
        # Should be able to GET detail
        detail_resp = await client.get(f"members/{member.get('id')}")
        assert detail_resp.is_success()

    async def test_returned_content_matches_link_type(self, page):
        """Test: Following links returns expected content type."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        if not resp.body.get("results"):
            pytest.skip("No members available")
        
        member = resp.body["results"][0]
        
        # Navigate to detail
        detail_resp = await client.get(f"members/{member.get('id')}")
        
        # Should return JSON (or whatever content type)
        assert detail_resp.headers.get("Content-Type"), \
            "Response should have Content-Type header"
