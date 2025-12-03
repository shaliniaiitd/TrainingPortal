import time
import jwt

class TokenManager:
    """
    Handles JWT authentication for Playwright API tests using Django Simple JWT.
    Automatically refreshes the access token when it expires.
    """

    def __init__(self, request_context, username, password):
        self.request_context = request_context
        self.username = username
        self.password = password

        self.access = None
        self.refresh = None
        self.access_exp = 0  # unix timestamp

    async def login(self):
        """Login using /api_async/token/ to obtain access + refresh tokens."""
        resp = await self.request_context.post(
            "/api_async/token/",
            data={"username": self.username, "password": self.password}
        )

        if resp.ok:
            data = await resp.json()
            self.access = data["access"]
            self.refresh = data["refresh"]
            self._decode_access()
        else:
            raise Exception(f"Login failed: {resp.status} {await resp.text()}")

    def _decode_access(self):
        """Decode JWT to get expiration timestamp (without verifying signature)."""
        payload = jwt.decode(
            self.access,
            options={"verify_signature": False}
        )
        self.access_exp = payload["exp"]

    def _is_access_expiring(self):
        """
        Returns True if access token expires in the next 30 seconds.
        Prevents mid-request failures in long tests.
        """
        now = int(time.time())
        return now >= self.access_exp - 30

    async def refresh_access(self):
        """Uses refresh token to obtain a new access token."""
        resp = await self.request_context.post(
            "/api_async/token/refresh/",
            data={"refresh": self.refresh}
        )

        if resp.ok:
            data = await resp.json()
            self.access = data["access"]
            self._decode_access()
        else:
            # Refresh token is expired → do a fresh login
            await self.login()

    async def get_access_token(self):
        """
        Returns a valid access token.
        Auto-refreshes if token is expired/expiring.
        """
        if self._is_access_expiring():
            await self.refresh_access()
        return self.access

    async def auth_headers(self):
        """
        Returns a complete authorization header to use in API requests.
        """
        token = await self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
