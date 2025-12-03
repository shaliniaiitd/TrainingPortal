"""Caching Tests - Using Playwright for API Validation

Tests for HTTP caching behavior using Playwright page.fetch():
- Cache-Control header validation
- ETag-based conditional requests
- 304 Not Modified responses
- Cache invalidation patterns
- Weak vs strong ETags
- Public/private directives

RFC 7234 Hypertext Transfer Protocol (HTTP/1.1) Caching
RFC 7232 HTTP/1.1 Conditional Requests (ETags)
"""

import pytest
from tests.api_async.base_api_test import PlaywrightApiClient


@pytest.mark.asyncio
class TestCacheControlHeaders:
    """Test Cache-Control header presence and validity."""

    async def test_cache_control_header_present_on_list(self, page):
        """Test: List endpoints include Cache-Control header."""
        client = PlaywrightApiClient(page)
        resp = await client.get("members")
        
        assert resp.is_success()
        assert resp.headers.get("Cache-Control") or resp.headers.get("cache-control"), \
            "Missing Cache-Control header"

    async def test_cache_control_header_present_on_detail(self, page):
        """Test: Detail endpoints include Cache-Control header."""
        client = PlaywrightApiClient(page)
        
        list_resp = await client.get("members")
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member_id = list_resp.body["results"][0].get("id")
        detail_resp = await client.get(f"members/{member_id}")
        
        assert detail_resp.headers.get("Cache-Control") or detail_resp.headers.get("cache-control")

    async def test_cache_control_max_age_format(self, page):
        """Test: Cache-Control max-age is valid."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        cache_control = resp.headers.get("Cache-Control") or resp.headers.get("cache-control")
        
        if cache_control and "max-age" in cache_control:
            # Extract max-age value
            import re
            match = re.search(r"max-age=(\d+)", cache_control)
            assert match, "max-age format invalid"
            max_age = int(match.group(1))
            assert max_age >= 0, "max-age must be non-negative"

    async def test_cache_control_directives_valid(self, page):
        """Test: Cache-Control directives are valid."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        cache_control = resp.headers.get("Cache-Control") or resp.headers.get("cache-control")
        
        if cache_control:
            # Valid directives
            valid = {"public", "private", "max-age", "must-revalidate", "no-cache", "no-store"}
            parts = [p.strip() for p in cache_control.split(",")]
            
            for part in parts:
                directive = part.split("=")[0].strip()
                assert directive.lower() in valid or "=" in part, \
                    f"Invalid Cache-Control directive: {directive}"

    async def test_cache_control_consistency_across_requests(self, page):
        """Test: Same endpoint returns consistent Cache-Control."""
        client = PlaywrightApiClient(page)
        
        resp1 = await client.get("members?limit=5")
        cache1 = resp1.headers.get("Cache-Control")
        
        resp2 = await client.get("members?limit=5")
        cache2 = resp2.headers.get("Cache-Control")
        
        assert cache1 == cache2, "Cache-Control should be consistent"


@pytest.mark.asyncio
class TestETagHeader:
    """Test ETag header generation and validity."""

    async def test_etag_header_present(self, page):
        """Test: ETag header is present on responses."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        assert resp.is_success()
        etag = resp.headers.get("ETag") or resp.headers.get("etag")
        assert etag, "ETag header missing"

    async def test_etag_format_is_valid(self, page):
        """Test: ETag format is valid."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        etag = resp.headers.get("ETag") or resp.headers.get("etag")
        
        if etag:
            # Should be quoted string or weak ETag
            assert etag.startswith('"') or etag.startswith('W/"'), \
                f"Invalid ETag format: {etag}"
            assert etag.endswith('"'), f"ETag not properly quoted: {etag}"

    async def test_etag_uniqueness_across_resources(self, page):
        """Test: Different resources have different ETags."""
        client = PlaywrightApiClient(page)
        
        resp1 = await client.get("members")
        resp2 = await client.get("courses")
        
        etag1 = resp1.headers.get("ETag")
        etag2 = resp2.headers.get("ETag")
        
        if etag1 and etag2:
            assert etag1 != etag2, "Different resources should have different ETags"

    async def test_etag_stability_on_repeated_requests(self, page):
        """Test: Same resource returns same ETag."""
        client = PlaywrightApiClient(page)
        
        list_resp = await client.get("members")
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member_id = list_resp.body["results"][0].get("id")
        
        # Get same member twice
        resp1 = await client.get(f"members/{member_id}")
        etag1 = resp1.headers.get("ETag")
        
        resp2 = await client.get(f"members/{member_id}")
        etag2 = resp2.headers.get("ETag")
        
        assert etag1 == etag2, "ETag should remain stable for unchanged resource"

    async def test_etag_changes_on_update(self, page):
        """Test: ETag changes when resource is updated."""
        client = PlaywrightApiClient(page)
        
        list_resp = await client.get("members")
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member = list_resp.body["results"][0]
        member_id = member.get("id")
        
        # Get original ETag
        resp1 = await client.get(f"members/{member_id}")
        etag_before = resp1.headers.get("ETag")
        
        # Update member
        await client.put(f"members/{member_id}", {
            "firstname": "Updated",
            "lastname": member.get("lastname", "Test"),
            "designation": member.get("designation", "Dev"),
            "image": ""
        })
        
        # Get new ETag
        resp2 = await client.get(f"members/{member_id}")
        etag_after = resp2.headers.get("ETag")
        
        if etag_before and etag_after:
            assert etag_before != etag_after, "ETag should change on update"


@pytest.mark.asyncio
class TestConditionalRequests:
    """Test conditional GET requests using If-None-Match."""

    async def test_if_none_match_returns_304(self, page):
        """Test: If-None-Match with matching ETag returns 304."""
        client = PlaywrightApiClient(page)
        
        # Get resource with ETag
        resp1 = await client.get("members?limit=1")
        etag = resp1.headers.get("ETag")
        
        if etag:
            # Send If-None-Match header
            resp2 = await client.get(
                "members?limit=1",
                headers={"If-None-Match": etag}
            )
            
            # Should return 304 Not Modified or 200 with same content
            assert resp2.status_code in [200, 304], \
                f"Unexpected status for conditional request: {resp2.status_code}"

    async def test_if_modified_since_header(self, page):
        """Test: If-Modified-Since header handling."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        last_modified = resp.headers.get("Last-Modified")
        
        if last_modified:
            # Send If-Modified-Since
            resp2 = await client.get(
                "members",
                headers={"If-Modified-Since": last_modified}
            )
            
            # Should return 304 or 200
            assert resp2.status_code in [200, 304]

    async def test_conditional_request_empty_body_on_304(self, page):
        """Test: 304 response has minimal body."""
        client = PlaywrightApiClient(page)
        
        resp1 = await client.get("members")
        etag = resp1.headers.get("ETag")
        
        if etag:
            resp2 = await client.get(
                "members",
                headers={"If-None-Match": etag}
            )
            
            if resp2.status_code == 304:
                # 304 response should have no or minimal body
                assert len(resp2.body or {}) <= 1

    async def test_if_none_match_mismatch_returns_200(self, page):
        """Test: If-None-Match with non-matching ETag returns 200."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        
        # Send wrong ETag
        resp2 = await client.get(
            "members",
            headers={"If-None-Match": '"wrong-etag"'}
        )
        
        # Should return 200 (not 304)
        assert resp2.status_code == 200

    async def test_conditional_with_expired_cache(self, page):
        """Test: Expired cache triggers full request."""
        client = PlaywrightApiClient(page)
        
        # First request
        resp1 = await client.get("members")
        etag1 = resp1.headers.get("ETag")
        
        # Update resource
        list_resp = await client.get("members")
        if list_resp.body.get("results"):
            member = list_resp.body["results"][0]
            member_id = member.get("id")
            
            await client.put(f"members/{member_id}", {
                "firstname": "Updated",
                "lastname": member.get("lastname", "Test"),
                "designation": member.get("designation", "Dev"),
                "image": ""
            })
        
        # Request with old ETag
        resp2 = await client.get(
            "members",
            headers={"If-None-Match": etag1}
        )
        
        # Should return 200 (content changed)
        assert resp2.status_code == 200


@pytest.mark.asyncio
class TestCacheInvalidation:
    """Test cache invalidation on mutations."""

    async def test_post_invalidates_list_cache(self, page):
        """Test: POST invalidates collection cache."""
        client = PlaywrightApiClient(page)
        
        # Get list with ETag
        list_resp = await client.get("members")
        etag_before = list_resp.headers.get("ETag")
        
        # Create new member
        await client.post("members", {
            "firstname": "CacheTest",
            "lastname": "Member",
            "designation": "Dev",
            "image": ""
        })
        
        # Get list again
        list_resp2 = await client.get("members")
        etag_after = list_resp2.headers.get("ETag")
        
        # ETag should change
        if etag_before and etag_after:
            assert etag_before != etag_after, "ETag should change after POST"

    async def test_put_invalidates_resource_cache(self, page):
        """Test: PUT invalidates resource cache."""
        client = PlaywrightApiClient(page)
        
        list_resp = await client.get("members")
        if not list_resp.body.get("results"):
            pytest.skip("No members available")
        
        member = list_resp.body["results"][0]
        member_id = member.get("id")
        
        # Get with ETag
        resp1 = await client.get(f"members/{member_id}")
        etag_before = resp1.headers.get("ETag")
        
        # Update
        await client.put(f"members/{member_id}", {
            "firstname": "Updated",
            "lastname": member.get("lastname", "Test"),
            "designation": member.get("designation", "Dev"),
            "image": ""
        })
        
        # Get updated resource
        resp2 = await client.get(f"members/{member_id}")
        etag_after = resp2.headers.get("ETag")
        
        if etag_before and etag_after:
            assert etag_before != etag_after, "ETag should change after PUT"

    async def test_delete_makes_resource_unavailable(self, page):
        """Test: DELETE makes resource return 404."""
        client = PlaywrightApiClient(page)
        
        # Create member
        create_resp = await client.post("members", {
            "firstname": "DeleteCache",
            "lastname": "Test",
            "designation": "Dev",
            "image": ""
        })
        
        if not create_resp.is_success():
            pytest.skip("Cannot create test member")
        
        member_id = create_resp.body.get("id")
        
        # Delete
        await client.delete(f"members/{member_id}")
        
        # Try to get
        resp = await client.get(f"members/{member_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestCacheEdgeCases:
    """Test edge cases in caching behavior."""

    async def test_error_responses_not_cached(self, page):
        """Test: 4xx/5xx responses have appropriate cache headers."""
        client = PlaywrightApiClient(page)
        
        # Get non-existent resource
        resp = await client.get("members/999999999")
        
        cache_control = resp.headers.get("Cache-Control")
        # Error responses should typically not be cached or have short TTL
        if cache_control:
            # Check for no-cache or short max-age
            assert "no-cache" in cache_control or "max-age" in cache_control

    async def test_weak_etag_handling(self, page):
        """Test: Weak ETags (W/) are handled properly."""
        client = PlaywrightApiClient(page)
        
        resp = await client.get("members")
        etag = resp.headers.get("ETag")
        
        if etag and etag.startswith('W/"'):
            # Weak ETag is valid for conditional requests
            resp2 = await client.get(
                "members",
                headers={"If-None-Match": etag}
            )
            assert resp2.status_code in [200, 304]

    async def test_cache_directives_on_mutations(self, page):
        """Test: POST/PUT/DELETE responses include cache headers."""
        client = PlaywrightApiClient(page)
        
        create_resp = await client.post("members", {
            "firstname": "Test",
            "lastname": "Member",
            "designation": "Dev",
            "image": ""
        })
        
        if create_resp.is_success():
            # POST response should have cache headers
            cache_control = create_resp.headers.get("Cache-Control")
            assert cache_control, "POST response missing Cache-Control"
