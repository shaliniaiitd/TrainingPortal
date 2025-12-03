import pytest
from playwright.sync_api import Page, APIRequestContext, expect

BASE = "http://localhost:8000/myapp/api_sync/members/"


"""
In standalone Playwright tests, api_request_context is built-in.
In Playwright + Django, it is not, so you must define your own fixture.

"""
# @pytest.fixture
# def api_request_context(page):
#     # Playwright exposes an API client via page.context.request
#     return page.context.request
#
# @pytest.fixture
# def api_context(page, django_user_model, api_request_context):
#     user = django_user_model.objects.create_user(username="test", password="pass")
#     token = Token.objects.create(user=user)
#
#     return page.request.new_context(extra_http_headers={
#         "Authorization": f"Token {token.key}"
#     })

@pytest.mark.django_db
def test_end_to_end_member_flow(page: Page, auth_context):
    """
    FULL END-TO-END TESTBASE
    1. Create Member in UI
    2. Validate in API
    3. Update via API
    4. Validate in UI
    5. Delete via API
    6. Validate removal in UI
    """
    import time
    # ------------------------------------------------------
    # 1. UI → CREATE MEMBER
    # ------------------------------------------------------
    page.goto("http://localhost:8000/myapp/members/addmember/")
    firstname = "first" + str(time.time())
    lastname = "last" + str(time.time())
    designation = "developer"


    page.fill("input[name=firstname]", firstname)
    page.fill("input[name=lastname]", lastname)
    page.fill("input[name=designation]", designation)

    # save form
    page.click("input[type='submit']")

    # Should redirect to members list
    print(page.url)
    expect(page).to_have_url("http://localhost:8000/myapp/members/")


    # UI now shows the member
    expect(page.locator(f"text='{firstname}'")).to_be_visible()

    # ------------------------------------------------------
    # 2. API → VERIFY CREATED MEMBER EXISTS
    # ------------------------------------------------------
    api_resp = auth_context.get(url = BASE)
    assert api_resp.ok

    members = api_resp.json()
    member = next((m for m in members if m["firstname"] == firstname and m["lastname"] == lastname), None)
    assert member is not None, "Member created in UI NOT found in API"
    member_id = member["id"]

    # ------------------------------------------------------
    # 3. API → UPDATE MEMBER
    # ------------------------------------------------------
    update = lastname+"Updated"
    update_payload = {
        "firstname": firstname,
        "lastname": update ,
        "designation": designation
    }

    update_resp = auth_context.put(f"{BASE}{member_id}/", data=update_payload)
    assert update_resp.ok

    # ------------------------------------------------------
    # 4. UI → VERIFY UPDATED MEMBER APPEARS
    # ------------------------------------------------------
    page.reload()
    expect(page.locator(f"text={update}")).to_be_visible()

    # ------------------------------------------------------
    # 5. API → DELETE MEMBER
    # ------------------------------------------------------
    del_resp = auth_context.delete(f"{BASE}{member_id}/")
    assert del_resp.status == 204

    # ------------------------------------------------------
    # 6. UI → VERIFY MEMBER REMOVED
    # ------------------------------------------------------
    page.reload()
    expect(page.locator(f"text='{firstname}'")).not_to_be_visible()
