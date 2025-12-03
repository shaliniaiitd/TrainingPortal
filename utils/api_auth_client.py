# utils/api_auth_client.py

import asyncio
from dataclasses import dataclass
from playwright.async_api import APIRequestContext

@dataclass
class TokenPair:
    access: str
    refresh: str


class APIAuthClient:
    """
    A reusable authenticated API client.
    Handles:
      - login
      - storing JWTs
      - refreshing expired access tokens
      - making authenticated calls
    """

    def __init__(self, request_context: APIRequestContext, base_url: str):
        self.request_context = request_context
        self.base_url = base_url
        self.token_pair: TokenPair | None = None

    # ------------------------------
    # LOGIN and TOKEN HANDLING
    # ------------------------------

    async def login(self, username: str, password: str):
        """Log in and store access & refresh tokens."""
        resp = await self.request_context.post(
            f"{self.base_url}/api_async/token/",
            data={"username": username, "password": password},
        )
        assert resp.status == 200, f"Login failed: {await resp.text()}"

        data = await resp.json()
        self.token_pair = TokenPair(
            access=data["access"],
            refresh=data["refresh"]
        )

    async def _refresh_access_token(self):
        """Automatically refresh an expired token."""
        resp = await self.request_context.post(
            f"{self.base_url}/api_async/token/refresh/",
            data={"refresh": self.token_pair.refresh}
        )

        assert resp.status == 200, f"Refresh token failed: {await resp.text()}"
        data = await resp.json()
        self.token_pair.access = data["access"]

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token_pair.access}"}

    # ------------------------------
    # CORE REQUEST WRAPPER
