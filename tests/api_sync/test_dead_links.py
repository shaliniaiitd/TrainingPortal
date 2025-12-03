ENDPOINTS = [
    "/myapp/api_sync/members/",
    "/myapp/api_sync/courses/",
    "/myapp/api_sync/students/",
    "/myapp/api_sync/users/",
]

def test_dead_links(auth_client):
    for ep in ENDPOINTS:
        resp = auth_client.get(ep)
        assert resp.status_code != 404, f"Dead link detected → {ep}"

