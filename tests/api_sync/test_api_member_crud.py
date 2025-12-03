import pytest

BASE = "/myapp/api_sync/members/"

@pytest.mark.django_db
def test_member_crud_flow(auth_client):
    # -----------------------
    # CREATE
    # -----------------------

    create_payload = {
        "firstname": "John",
        "lastname": "Doe",
        "designation": "Developer",
    }

    resp = auth_client.post(BASE, create_payload, format="json")
    assert resp.status_code == 201, resp.content

    member_id = resp.data["id"]

    # -----------------------
    # READ
    # -----------------------
    resp = auth_client.get(f"{BASE}{member_id}/")
    assert resp.status_code == 200
    assert resp.data["firstname"] == "John"

    # -----------------------
    # UPDATE
    # -----------------------
    update_payload = {
        "firstname": "Edward",
        "lastname": "Doe",
        "designation": "Developer"
    }

    resp = auth_client.put(f"{BASE}{member_id}/", update_payload, format="json")
    assert resp.status_code in (200, 202)
    assert resp.data["firstname"] == "Edward"

    # -----------------------
    # DELETE
    # -----------------------
    resp = auth_client.delete(f"{BASE}{member_id}/")
    assert resp.status_code in (204, 200)

    # -----------------------
    # VERIFY DELETE
    # -----------------------
    resp = auth_client.get(f"{BASE}{member_id}/")
    assert resp.status_code == 404
