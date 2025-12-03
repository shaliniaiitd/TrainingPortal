import pytest
import json
import allure

BASE = "/myapp/api_async/members/"

@allure.feature("Members API")
@allure.story("Create Member")

@pytest.mark.asyncio
async def test_create_member(request_context, auth_headers):
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "designation": "Trainer"
    }

    with allure.step("Send POST request to create member"):
        resp = await request_context.post(BASE, headers=auth_headers, data=json.dumps(payload))
        assert resp.status == 201

    with allure.step("Validate returned ID"):
        data = await resp.json()
        global created_id
        created_id = data["id"]


@pytest.mark.asyncio
async def test_get_member(request_context, auth_headers):
    resp = await request_context.get(f"{BASE}{created_id}/", headers=auth_headers)
    assert resp.status == 200


@pytest.mark.asyncio
async def test_update_member(request_context, auth_headers):
    payload = {
        "firstname": "Johnny",
        "lastname": "Doe",
        "designation": "Senior Trainer"
    }

    resp = await request_context.put(f"{BASE}{created_id}/", headers=auth_headers, data=json.dumps(payload))
    assert resp.ok


@pytest.mark.asyncio
async def test_delete_member(request_context, auth_headers):
    resp = await request_context.delete(f"{BASE}{created_id}/", headers=auth_headers)
    assert resp.status in [200, 204]
