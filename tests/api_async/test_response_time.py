import pytest
import time

@pytest.mark.asyncio
async def test_members_response_time(request_context, auth_headers):
    start = time.time()
    resp = await request_context.get("/myapp/api_async/members/", headers=auth_headers)
    end = time.time()

    assert resp.ok
    assert (end - start) < 0.5, "Response took longer than 500ms"
