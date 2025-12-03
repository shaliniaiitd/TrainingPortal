import pytest
@pytest.mark.asyncio
async def test_get_members_authenticated(auth_client):
    resp = await auth_client.get("/myapp/api_async/members/")
    assert resp.status == 200

@pytest.mark.asyncio
async def test_unauthorized_blocked(request):
    # No JWT token
    resp = await request.get("/myapp/api_async/members/")
    assert resp.status == 401