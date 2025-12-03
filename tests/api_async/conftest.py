# # tests/api_async/conftest.py
#
# import pytest
# from playwright.async_api import Playwright
# from utils.api_auth_client import APIAuthClient
#
# BASE_URL = "http://127.0.0.1:8000/myapp"
#
# import pytest
#
# # Prevent pytest-asyncio from creating its own event loop
# @pytest.fixture(scope="session")
# def event_loop():
#     import asyncio
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()
#
# @pytest.fixture(scope="function")
# async def request_context(playwright: Playwright):
#     """
#     Creates a shared Playwright APIRequestContext for the entire test session.
#     This is like requests.Session() — persistent and fast.
#     """
#     context = await playwright.request.new_context(
#         base_url=BASE_URL,
#         extra_http_headers={
#             "Content-Type": "application/json"
#         }
#     )
#     yield context
#     await context.dispose()
#
#
# @pytest.fixture(scope="function")
# async def auth_client(request_context):
#     """
#     Returns a fully authenticated client.
#     Auto-refreshes JWT token when it expires.
#     """
#     client = APIAuthClient(request_context, BASE_URL)
#
#     # ---- Login user here ----
#     await client.login(
#         username="admin",
#         password="adminpass"
#     )
#
#     return client
