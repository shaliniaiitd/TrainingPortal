# utils/config.py
# Simple central place for environment and API config used by tests & clients.

import os

# Base application URL (overridable via env var)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

# API prefixes / endpoints
API_PREFIX = os.getenv("API_PREFIX", "/myapp/api_async")
TOKEN_URL = os.getenv("TOKEN_URL", "/api_async/token/")
REFRESH_URL = os.getenv("REFRESH_URL", "/api_async/token/refresh/")

# Default credentials for test automation (use GitHub Secrets / env in CI)
TEST_USERNAME = os.getenv("TEST_USERNAME", "admin")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "admin123")

# Timeouts / thresholds
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
SLA_RESPONSE_SECONDS = float(os.getenv("SLA_RESPONSE_SECONDS", "0.5"))

# Allure / Reports dir
ALLURE_RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", "allure-results")
