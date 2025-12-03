import pytest
import time

ENDPOINTS = [
    "/myapp/api_async/members/",
    "/myapp/api_async/courses/",
    "/myapp/api_async/students/",
    "/myapp/api_async/users/",
]


async def test_dead_links(auth_client):
    """Ensure none of the API endpoints return 404."""
    for ep in ENDPOINTS:
        resp = await auth_client.get(ep)
        assert resp.status != 404, f"Dead link detected: {ep}"


async def test_members_response_time(request_context, auth_client):
    """Basic response-time test."""
    start = time.perf_counter()
    resp = await request_context.get("/myapp/api_async/members/")
    duration = time.perf_counter() - start

    assert resp.ok
    assert duration < 0.5, f"Slow response: {duration:.3f}s"


async def test_api_timing(request_context):
    """Accurate perf test using perf_counter."""
    start = time.perf_counter()
    resp = await request_context.get("https://example.com/api/users")
    duration = (time.perf_counter() - start) * 1000

    assert resp.status < 500
    print(f"API responded in {duration:.2f} ms")


async def test_rate_limit(request_context):
    """If throttling is enabled, should return 429 after several hits."""
    resp = None
    for _ in range(20):
        resp = await request_context.get("/myapp/api_async/members/")

    assert resp.status in [200, 429]
