# import pytest
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken
# import os
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
#
#
#
# @pytest.fixture
# def api_client():
#     """Returns a DRF APIClient instance."""
#     return APIClient()
#
# @pytest.fixture
# def auth_client(api_client, db):
#     #db(built in fixture- gets db access to Django's User model  '
#     """
#     Creates a superuser, generates a JWT token, and returns
#     an authenticated API client.
#     """
#     User = get_user_model()
#     user = User.objects.create_superuser(
#         username="admin",
#         email="admin@example.com",
#         password="admin123"
#     )
#
#     # Generate JWT token
#     refresh = RefreshToken.for_user(user)
#     token = str(refresh.access_token)
#
#     # Authenticate APIClient with JWT token
#     api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
#     return api_client
#
# import pytest
# from playwright.sync_api import Playwright
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import get_user_model
#
# """For unauthenticated tests if any to be conducted, right now not in use"""
# @pytest.fixture
# def api_context(playwright: Playwright):
#     """Unauthenticated Playwright API client."""
#     return playwright.request.new_context(base_url="http://localhost:8000")
#
#
# @pytest.fixture
# def auth_context(playwright: Playwright, db):
#     """Authenticated Playwright API client using JWT."""
#     User = get_user_model()
#
#     user = User.objects.create_superuser(
#         username="admin2",
#         email="admin@example.com",
#         password="admin123"
#     )
#
#     # Generate JWT
#     refresh = RefreshToken.for_user(user)
#     access = str(refresh.access_token)
#
#     return playwright.request.new_context(
#         base_url="http://localhost:8000",
#         extra_http_headers={
#             "Authorization":f"Bearer {access}",
#             "Content-Type": "application/json"
#         }
#     )
#
