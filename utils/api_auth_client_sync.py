# utils/api_auth_client_sync.py

from playwright.sync_api import APIRequestContext


class APIAuthClient:
    def __init__(self, request_context: APIRequestContext, base_url: str):
        self.request_context = request_context
        self.base_url = base_url
        self.access_token = None

    def login(self, username: str, password: str):
        resp = self.request_context.post(
            "/api/token/",
            data={"username": username, "password": password}
        )
        assert resp.ok, f"Login failed: {resp.status}"

        data = resp.json()
        self.access_token = data["access"]

    def get(self, url: str):
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        return self.request_context.get(url, headers=headers)
