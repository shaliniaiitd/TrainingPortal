

import pytest
import time
from concurrent.futures import ThreadPoolExecutor

ENDPOINTS = [
    "/myapp/api_sync/members/",
     "/myapp/api_sync/courses/",
     "/myapp/api_sync/students/",
     "/myapp/api_sync/users/",
]

# -----------------------------
# Basic dead link check
# -----------------------------
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("ep", ENDPOINTS)
def test_dead_links_concurrent(auth_client ,ep):

    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     results = list(executor.map(lambda _: get_request(auth_client,ep), range(10)))

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: auth_client.get( ep).status_code, range(10)))

    for status in results:
        assert status != 404, f"Dead link detected concurrently on {ep}"

@pytest.mark.parametrize("ep", ENDPOINTS)
def test_dead_links(auth_client,ep):
    # for ep in ENDPOINTS:
        resp = auth_client.get(ep)
        assert resp.status_code != 404, f"Dead link detected → {ep}"


# -----------------------------
# Rate limiting check
# -----------------------------
@pytest.mark.parametrize("ep", ENDPOINTS)
def test_rate_limiting(auth_client,ep):
    ep = ENDPOINTS[0]
    max_requests = 20
    for _ in range(max_requests):
        resp = auth_client.get(ep)
        assert resp.status_code != 429, f"Rate limit triggered too early on {ep}"


# -----------------------------
# Concurrency check
# -----------------------------
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("ep", ENDPOINTS)
def test_concurrent_requests(auth_client,ep):
    #ep = ENDPOINTS[0]
    num_threads = 10

    def get_request():
        resp = auth_client.get(ep)
        return resp.status_code

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(lambda _: auth_client.get(ep).status_code, range(num_threads)))

    for status in results:
        assert status < 500, f"Server error under concurrent requests: {status}"


# -----------------------------
# Combined caching & stress test
# -----------------------------
@pytest.mark.parametrize("ep", ENDPOINTS)
def test_caching_and_stress(auth_client,ep):
    #ep = ENDPOINTS[0]
    iterations = 10
    times = []

    for _ in range(iterations):
        start = time.time()
        resp = auth_client.get(ep)
        elapsed = time.time() - start
        times.append(elapsed)
        assert resp.status_code == 200

    # Check if caching has effect (second request should be faster than first)
    if iterations > 1:
        assert times[1] <= times[0], "Caching does not seem effective"

    avg_time = sum(times) / len(times)
    print(f"{iterations} requests to {ep} completed, avg response time: {avg_time:.2f}s")


# -----------------------------
# Response time check
# -----------------------------
@pytest.mark.parametrize("ep", ENDPOINTS)
def test_response_time(auth_client, ep):
    max_allowed_time = 10.0  # seconds
    resp = auth_client.get(ep)
    elapsed = resp.elapsed.total_seconds()
    assert elapsed <= max_allowed_time, f"{ep} is slow: {elapsed:.2f}s"
