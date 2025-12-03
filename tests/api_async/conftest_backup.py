"""
Pytest Configuration for TrainingPortal Tests

Comprehensive pytest configuration featuring:
- Async test support (asyncio)
- Parallel execution (pytest-xdist)
- Test timeouts
- Custom markers and fixtures
- Logging configuration
- Integration with test_config.py
"""

import pytest
import asyncio
from pathlib import Path
from typing import Generator
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging
from datetime import datetime
import sys
import os

from utils.auth_client import get_jwt_token
from utils.api_auth_client import APIAuthClient

from utils.token_manager import TokenManager
from utils.config import BASE_URL

@pytest.fixture(scope="session")
async def token_manager(request_context):
    tm = TokenManager(
        request_context,
        username="superuser",       # your DRF user
        password="password123"     # your DRF password
    )
    await tm.login()
    return tm


@pytest.fixture
async def auth_client(request):
    token = await get_jwt_token(request, "admin", "adminpassword")
    return APIAuthClient(request, token)

@pytest.fixture
async def auth_headers(token_manager):
    return await token_manager.auth_headers()

# Add tests directory to path for config import
# sys.path.insert(0, str(Path(__file__).parent.parent))
# from test_config import DEFAULT_CONFIG
#
# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('test_execution.log'),
#         logging.StreamHandler()
#     ]
# )
#
# logger = logging.getLogger(__name__)
#
#
# def pytest_configure(config):
#     """Configure pytest with markers and settings."""
#     config.addinivalue_line(
#         "markers", "asyncio: mark test as async"
#     )
#     config.addinivalue_line(
#         "markers", "integration: mark test as integration test"
#     )
#     config.addinivalue_line(
#         "markers", "unit: mark test as unit test"
#     )
#     config.addinivalue_line(
#         "markers", "slow: mark test as slow running"
#     )
#     config.addinivalue_line(
#         "markers", "critical: mark test as critical path"
#     )
#     config.addinivalue_line(
#         "markers", "api_async: mark test as API test"
#     )
#     config.addinivalue_line(
#         "markers", "ui: mark test as UI test"
#     )
#     config.addinivalue_line(
#         "markers", "smoke: mark test as smoke test"
#     )
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     """Create event loop for async tests."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture(scope="session")
# async def browser():
#     """Provide browser instance for test session.
#
#     Uses browser configuration from test_config.py
#     """
#     browser_config = DEFAULT_CONFIG.browser
#
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=browser_config.headless,
#             args=browser_config.args,
#             slow_mo=browser_config.slow_motion
#         )
#         logger.info(f"Browser launched: {browser_config.browser_type} (headless={browser_config.headless})")
#         yield browser
#         await browser.close()
#         logger.info("Browser closed")
#
#
# @pytest.fixture
# async def context(browser):
#     """Provide browser context for each test.
#
#     Creates isolated context per test for better parallelization.
#     """
#     context = await browser.new_context(
#         ignore_https_errors=DEFAULT_CONFIG.browser.ignore_https_errors
#     )
#     yield context
#     await context.close()
#
#
# @pytest.fixture
# async def page(context: BrowserContext) -> Generator[Page, None, None]:
#     """Provide page instance for each test.
#
#     Yields:
#         Playwright Page instance configured from test_config.py
#     """
#     page = await context.new_page()
#
#     # Set timeout from config
#     page.set_default_timeout(DEFAULT_CONFIG.browser.timeout)
#     page.set_default_navigation_timeout(DEFAULT_CONFIG.browser.timeout)
#
#     logger.info(f"Page created for test")
#
#     yield page
#
#     await page.close()
#     logger.info(f"Page closed")
#
#
# def pytest_collection_modifyitems(config, items):
#     """Modify test collection to add markers and configure asyncio."""
#     for item in items:
#         # Auto-mark async tests
#         if asyncio.iscoroutinefunction(item.function):
#             item.add_marker(pytest.mark.asyncio)
#
#         # Add marker based on file path
#         if 'integration' in str(item.fspath):
#             item.add_marker(pytest.mark.integration)
#         elif 'unit' in str(item.fspath):
#             item.add_marker(pytest.mark.unit)
#
#         # Add API/UI markers based on directory
#         if '/api_async/' in str(item.fspath):
#             item.add_marker(pytest.mark.api_async)
#         elif '/ui/' in str(item.fspath):
#             item.add_marker(pytest.mark.ui)
#
#         # Add timeout marker from config
#         item.add_marker(pytest.mark.timeout(DEFAULT_CONFIG.parallel.test_timeout))
#
#
# def pytest_runtest_setup(item):
#     """Setup test run."""
#     logger.info(f"Starting test: {item.name}")
#
#
# def pytest_runtest_makereport(item, call):
#     """Create test report."""
#     if call.when == "call":
#         logger.info(f"Test {item.name} - {call.outcome}")
#
#
# @pytest.fixture(autouse=True)
# def setup_test_logging(request):
#     """Setup logging for each test."""
#     logger.info(f"{'='*60}")
#     logger.info(f"Test: {request.node.name}")
#     logger.info(f"Time: {datetime.now().isoformat()}")
#     logger.info(f"{'='*60}")
#
#     yield
#
#     logger.info(f"Test completed: {request.node.name}")
#
#
# @pytest.fixture
# def test_config():
#     """Provide test configuration from central config file.
#
#     Returns:
#         TestConfig instance with all settings
#     """
#     return DEFAULT_CONFIG
#
#
# @pytest.fixture
# def test_data():
#     """Provide test data with URLs from central configuration.
#
#     Returns:
#         Dictionary with URLs and sample test data
#     """
#     config = DEFAULT_CONFIG
#     return {
#         # URLs - Updated to use /myapp path
#         'base_url': config.urls.base_url,
#         'web_url': config.urls.web_url,  # http://127.0.0.1:8000/myapp
#         'api_base_url': config.urls.api_base_url,  # http://127.0.0.1:8000/myapp/api
#
#         # Valid test data for Members
#         'valid_member': {
#             'designation': 'Senior Developer',
#             'description': 'Test Member'
#         },
#
#         # Valid test data for Courses
#         'valid_course': {
#             'course_name': 'Test Course',
#             'category': 'P',  # Programming
#             'duration': 40,
#             'fees': 500.00
#         },
#
#         # Valid test data for Students
#         'valid_student': {
#             'name': 'Test Student',
#             'email': 'student@test.com',
#             'resume': 'https://example.com/resume.pdf',
#             'skills': 'Python, Django'
#         }
#     }
#
#
# # Pytest configuration options
# def pytest_addoption(parser):
#     """Add custom command line options."""
#     parser.addoption(
#         "--workers",
#         action="store",
#         default=4,
#         type=int,
#         help="Number of parallel workers for pytest-xdist"
#     )
#     parser.addoption(
#         "--headless",
#         action="store_true",
#         default=True,
#         help="Run tests in headless mode"
#     )
#     parser.addoption(
#         "--slow",
#         action="store_true",
#         help="Include slow tests"
#     )
#     parser.addoption(
#         "--critical-only",
#         action="store_true",
#         help="Run only critical tests"
#     )
#     parser.addoption(
#         "--preset",
#         action="store",
#         choices=['fast', 'full', 'ci', 'debug', 'performance'],
#         help="Use configuration preset"
#     )
#
#
# # def pytest_configure_new_session(config):
# #     """Configure new test session based on options."""
# #     if config.getoption("--critical-only"):
# #         config.option.markexpr = "critical"
# #     elif not config.getoption("--slow"):
# #         config.option.markexpr = "not slow"
