import pytest

BASE = "/myapp/api_async/members/"

@pytest.mark.asyncio
async def test_get_nonexistent_member(request_context, auth_headers):
    resp = await request_context.get(f"{BASE}99999/", headers=auth_headers)
    assert resp.status == 404
