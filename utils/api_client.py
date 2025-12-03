import json
from utils.config import BASE_URL, TOKEN_URL, REFRESH_URL, TEST_USERNAME, TEST_PASSWORD

# when you create a request context:
request_context = playwright.request.new_context(base_url=BASE_URL)
# and use TOKEN_URL, REFRESH_URL to login/refresh

import json

async def get_jwt_token(request, username, password):
    resp = await request.post("/api_async/token/", data=json.dumps({
        "username": username,
        "password": password
    }))

    assert resp.status == 200, "JWT Login failed"
    tokens = await resp.json()
    return tokens["access"]


class AuthAPIClient:
    def __init__(self, request, token):
        self.request = request
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def get(self, endpoint):
        return await self.request.get(endpoint, headers=self.headers)

    async def post(self, endpoint, data):
        return await self.request.post(endpoint, data=json.dumps(data), headers=self.headers)

    async def put(self, endpoint, data):
        return await self.request.put(endpoint, data=json.dumps(data), headers=self.headers)

    async def delete(self, endpoint):
        return await self.request.delete(endpoint, headers=self.headers)
