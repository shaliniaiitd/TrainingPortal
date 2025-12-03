import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://jsonplaceholder.typicode.com"  # Dummy API

@pytest.fixture(scope="session")
def api_context():
    with sync_playwright() as p:
        request_context = p.request.new_context(base_url=BASE_URL)
        yield request_context
        request_context.dispose()


# ----------------- CREATE -----------------
def test_create_member(api_context, request):
    payload = {

"firstname": "first1",
"lastname": "last1",
"designation": "d1",

}
    response = api_context.post("/users", data=payload)
    assert response.ok
    data = response.json()
    request.cls.set('member_data') = data  # Store member data for other tests


# ----------------- READ -----------------
def test_get_member(api_context, request):
    member_id = request.cls.member_data[0]["id"]
    assert member_id is not None
    response = api_context.get(f"/users/{member_id}")
    assert response.ok
    assert member_data == response.json()


# ----------------- UPDATE -----------------
def test_update_member(api_context, member_data):
    member_id = member_data.get('id')
    assert member_id is not None
    payload = {
        "name": "John Updated",
        "email": "john_updated@example.com"
    }
    response = api_context.put(f"/users/{member_id}", data=payload)
    assert response.ok
    data = response.json()
    print("Updated member data:", data)

# ----------------- DELETE -----------------
def test_delete_member(api_context, member_data):
    member_id = member_data.get('id')
    assert member_id is not None
    response = api_context.delete(f"/users/{member_id}")
    assert response.ok
    print("Deleted member ID:", member_id)



