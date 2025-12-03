"""Base API Test Class using Playwright - API validations through browser automation

Provides:
- Playwright-based HTTP client using page.fetch()
- Response validation framework with fluent chaining
- Comprehensive 429 (Too Many Requests) rate limit handling
- Exponential backoff and retry strategies
- All HTTP methods: GET, POST, PUT, PATCH, DELETE

Advantages of Playwright approach:
- Tests real API responses through browser context
- Can validate headers, cookies, timing
- Full browser context (user-agent, auth cookies, etc.)
- Single test framework for UI and API
- Better integration testing (full request/response cycle)

Usage:
    async def test_example(page):
        client = PlaywrightApiClient(page)
        resp = await client.get("members")
        assert resp.is_success()
"""

import pytest
import time
import random
import json
import re
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class HttpMethod(Enum):
    """HTTP method enum."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class ApiResponse:
    """Encapsulates API response data from Playwright fetch."""
    status_code: int
    body: Dict[str, Any]
    headers: Dict[str, str]
    elapsed_ms: float
    retry_count: int = 0
    was_rate_limited: bool = False

    def is_success(self) -> bool:
        """Check if response is 2xx."""
        return 200 <= self.status_code < 300

    def is_client_error(self) -> bool:
        """Check if response is 4xx."""
        return 400 <= self.status_code < 500

    def is_server_error(self) -> bool:
        """Check if response is 5xx."""
        return 500 <= self.status_code < 600

    def is_rate_limited(self) -> bool:
        """Check if response is 429 Too Many Requests."""
        return self.status_code == 429

    def get_retry_after_seconds(self) -> Optional[float]:
        """Extract Retry-After header (seconds or HTTP-date).
        
        Returns:
            - float: seconds to wait if Retry-After is numeric
            - None: if header not present
            
        Handles both formats per RFC 7231:
        - Retry-After: 120 (delta-seconds)
        - Retry-After: Wed, 21 Oct 2025 07:28:00 GMT (HTTP-date)
        """
        retry_after = self.headers.get("Retry-After", self.headers.get("retry-after"))
        if not retry_after:
            return None
        
        try:
            # Try parsing as integer (delta-seconds)
            return float(retry_after)
        except ValueError:
            # Try parsing as HTTP-date
            try:
                retry_date = datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S %Z")
                delta = (retry_date - datetime.utcnow()).total_seconds()
                return max(0, delta)
            except ValueError:
                return None


class ResponseValidator:
    """Validates API responses against expected conditions using fluent chaining."""

    def __init__(self, response: ApiResponse):
        self.response = response

    def assert_status_code(self, expected: int) -> "ResponseValidator":
        """Assert response status code."""
        assert self.response.status_code == expected, \
            f"Expected status {expected}, got {self.response.status_code}. Body: {self.response.body}"
        return self

    def assert_status_2xx(self) -> "ResponseValidator":
        """Assert response is successful (2xx)."""
        assert self.response.is_success(), \
            f"Expected 2xx status, got {self.response.status_code}. Body: {self.response.body}"
        return self

    def assert_status_4xx(self) -> "ResponseValidator":
        """Assert response is client error (4xx)."""
        assert self.response.is_client_error(), \
            f"Expected 4xx status, got {self.response.status_code}"
        return self

    def assert_status_5xx(self) -> "ResponseValidator":
        """Assert response is server error (5xx)."""
        assert self.response.is_server_error(), \
            f"Expected 5xx status, got {self.response.status_code}"
        return self

    def assert_not_rate_limited(self) -> "ResponseValidator":
        """Assert response is NOT 429 rate limited."""
        assert not self.response.is_rate_limited(), \
            f"Request was rate limited (429). Retry-After: {self.response.get_retry_after_seconds()}s"
        return self

    def assert_rate_limited(self) -> "ResponseValidator":
        """Assert response IS 429 rate limited."""
        assert self.response.is_rate_limited(), \
            f"Expected 429 rate limit, got {self.response.status_code}"
        return self

    def assert_has_key(self, key: str) -> "ResponseValidator":
        """Assert response body has a key."""
        assert key in self.response.body, \
            f"Expected key '{key}' in response. Available: {self.response.body.keys()}"
        return self

    def assert_has_keys(self, keys: List[str]) -> "ResponseValidator":
        """Assert response body has multiple keys."""
        for key in keys:
            self.assert_has_key(key)
        return self

    def assert_key_equals(self, key: str, value: Any) -> "ResponseValidator":
        """Assert response key equals value."""
        self.assert_has_key(key)
        actual = self.response.body[key]
        assert actual == value, \
            f"Expected {key}={value}, got {key}={actual}"
        return self

    def assert_key_contains(self, key: str, substring: str) -> "ResponseValidator":
        """Assert response key contains substring."""
        self.assert_has_key(key)
        actual = str(self.response.body[key])
        assert substring.lower() in actual.lower(), \
            f"Expected '{key}' to contain '{substring}', got: {actual}"
        return self

    def assert_is_list(self, key: Optional[str] = None) -> "ResponseValidator":
        """Assert response (or key) is a list."""
        target = self.response.body[key] if key else self.response.body
        assert isinstance(target, list), \
            f"Expected list, got {type(target)}"
        return self

    def assert_list_length(self, expected_len: int, key: Optional[str] = None) -> "ResponseValidator":
        """Assert list length."""
        target = self.response.body[key] if key else self.response.body
        assert isinstance(target, list), f"Expected list"
        assert len(target) == expected_len, \
            f"Expected list length {expected_len}, got {len(target)}"
        return self

    def assert_list_length_gte(self, min_len: int, key: Optional[str] = None) -> "ResponseValidator":
        """Assert list length >= min_len."""
        target = self.response.body[key] if key else self.response.body
        assert isinstance(target, list), f"Expected list"
        assert len(target) >= min_len, \
            f"Expected list length >= {min_len}, got {len(target)}"
        return self

    def assert_header_present(self, header_name: str) -> "ResponseValidator":
        """Assert response header is present."""
        assert header_name in self.response.headers, \
            f"Expected header '{header_name}'. Available: {self.response.headers.keys()}"
        return self

    def assert_response_time_ms(self, max_ms: float) -> "ResponseValidator":
        """Assert response time is within threshold."""
        assert self.response.elapsed_ms <= max_ms, \
            f"Expected response time <= {max_ms}ms, got {self.response.elapsed_ms}ms"
        return self


@dataclass
class RateLimitMetrics:
    """Metrics for rate limit handling and retry behavior."""
    total_rate_limited: int = 0
    total_retries: int = 0
    total_backoff_seconds: float = 0.0
    max_backoff_seconds: float = 0.0
    rate_limit_timestamps: List[datetime] = field(default_factory=list)

    def record_rate_limit(self, backoff_seconds: float):
        """Record a rate limit event."""
        self.total_rate_limited += 1
        self.total_backoff_seconds += backoff_seconds
        self.max_backoff_seconds = max(self.max_backoff_seconds, backoff_seconds)
        self.rate_limit_timestamps.append(datetime.now())

    def record_retry(self):
        """Record a retry attempt."""
        self.total_retries += 1

    def __str__(self) -> str:
        """Summary of rate limit metrics."""
        return (
            f"RateLimitMetrics("
            f"rate_limited={self.total_rate_limited}, "
            f"total_retries={self.total_retries}, "
            f"total_backoff_seconds={self.total_backoff_seconds:.2f}, "
            f"max_backoff_seconds={self.max_backoff_seconds:.2f})"
        )


class PlaywrightApiClient:
    """Playwright-based HTTP client for API testing with rate limit handling.

    Uses page.fetch() for true browser-based HTTP requests with:
    - Rate limiting (429) automatic retry
    - Exponential backoff with jitter
    - Circuit breaker pattern
    - RFC 7231 Retry-After header support
    
    Example:
        async def test_api(page):
            client = PlaywrightApiClient(page)
            resp = await client.get("members")
            assert resp.is_success()
    """

    BASE_URL = "http://127.0.0.1:8000"
    API_PREFIX = "/api_async"
    
    # Rate limiting configuration
    MAX_RETRIES = 3
    INITIAL_BACKOFF_SECONDS = 1.0
    MAX_BACKOFF_SECONDS = 30.0
    BACKOFF_MULTIPLIER = 2.0
    ENABLE_JITTER = True
    CIRCUIT_BREAKER_THRESHOLD = 5

    def __init__(self, page):
        """Initialize with Playwright page object.
        
        Args:
            page: Playwright Page object for making fetch requests
        """
        self.page = page
        self.metrics = RateLimitMetrics()
        self.consecutive_rate_limits = 0

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        attempt: int = 0
    ) -> ApiResponse:
        """Make HTTP request using Playwright page.fetch().
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path
            data: Request body (auto-converted to JSON)
            headers: Additional headers to send
            attempt: Current retry attempt number
            
        Returns:
            ApiResponse with status, body, headers, timing
        """
        # Build URL
        url = f"{self.BASE_URL}{self.API_PREFIX}/{endpoint}"
        
        # Prepare headers
        request_headers = headers or {}
        request_headers["Content-Type"] = "application/json"
        
        # Prepare fetch options
        fetch_options = {
            "method": method,
            "headers": request_headers
        }
        
        # Add body if present
        if data is not None:
            fetch_options["body"] = json.dumps(data)
        
        try:
            # Time the request
            start_time = time.time()
            
            # Make request using Playwright
            response = await self.page.fetch(url, **fetch_options)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Extract response details
            status_code = response.status
            headers_dict = dict(await response.all_headers())
            
            # Parse body as JSON
            try:
                body_text = await response.text()
                body = json.loads(body_text) if body_text else {}
            except json.JSONDecodeError:
                body = {}
            
            # Create response object
            api_response = ApiResponse(
                status_code=status_code,
                body=body,
                headers=headers_dict,
                elapsed_ms=elapsed_ms,
                retry_count=attempt
            )
            
            # Handle 429 rate limiting
            if status_code == 429:
                return await self._handle_rate_limit(
                    method, endpoint, data, headers, attempt, api_response
                )
            
            # Reset circuit breaker on success
            self.consecutive_rate_limits = 0
            
            return api_response
            
        except Exception as e:
            # Network or parsing error
            raise Exception(f"API request failed: {str(e)}")

    async def _handle_rate_limit(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]],
        attempt: int,
        response: ApiResponse
    ) -> ApiResponse:
        """Handle 429 rate limit response with retry logic.
        
        Implements:
        - Exponential backoff
        - Jitter (±20% randomness)
        - Circuit breaker (fail-fast after N consecutive 429s)
        - RFC 7231 Retry-After header parsing
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body
            headers: Request headers
            attempt: Current attempt number
            response: The 429 response
            
        Returns:
            ApiResponse (either retry result or final 429)
        """
        self.consecutive_rate_limits += 1
        self.metrics.record_rate_limit(0)  # Will update with actual backoff
        
        # Circuit breaker: fail-fast if too many consecutive 429s
        if self.consecutive_rate_limits >= self.CIRCUIT_BREAKER_THRESHOLD:
            response.was_rate_limited = True
            return response
        
        # Check if max retries exceeded
        if attempt >= self.MAX_RETRIES:
            response.was_rate_limited = True
            return response
        
        # Calculate backoff time
        retry_after = response.get_retry_after_seconds()
        
        if retry_after is not None:
            # Use Retry-After header
            backoff_seconds = min(retry_after, self.MAX_BACKOFF_SECONDS)
        else:
            # Calculate exponential backoff
            backoff_seconds = self.INITIAL_BACKOFF_SECONDS * \
                             (self.BACKOFF_MULTIPLIER ** attempt)
            backoff_seconds = min(backoff_seconds, self.MAX_BACKOFF_SECONDS)
        
        # Add jitter (±20%) to prevent thundering herd
        if self.ENABLE_JITTER:
            jitter = random.uniform(0.8, 1.2)
            backoff_seconds *= jitter
        
        # Record backoff
        self.metrics.record_retry()
        self.metrics.total_backoff_seconds += backoff_seconds
        
        # Wait before retry
        await self.page.wait_for_timeout(backoff_seconds * 1000)
        
        # Retry the request
        return await self._make_request(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
            attempt=attempt + 1
        )

    async def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """GET request."""
        return await self._make_request("GET", endpoint, headers=headers)

    async def post(self, endpoint: str, data: Dict[str, Any], 
                   headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """POST request."""
        return await self._make_request("POST", endpoint, data=data, headers=headers)

    async def put(self, endpoint: str, data: Dict[str, Any],
                  headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """PUT request."""
        return await self._make_request("PUT", endpoint, data=data, headers=headers)

    async def patch(self, endpoint: str, data: Dict[str, Any],
                    headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """PATCH request."""
        return await self._make_request("PATCH", endpoint, data=data, headers=headers)

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """DELETE request."""
        return await self._make_request("DELETE", endpoint, headers=headers)


class BaseApiTestClass:
    """Legacy sync wrapper around async PlaywrightApiClient.
    
    For backward compatibility with existing test structure.
    Can be used in both async and sync test contexts.
    """

    # def __init__(self, page=None):
    #     """Initialize with optional page object.
    #
    #     Args:
    #         page: Playwright Page object (will be provided by fixture)
    #     """
    #     self.page = page
    #     self.client = None

    def _get_client(self):
        """Get or create Playwright API client."""
        if self.client is None and self.page is not None:
            self.client = PlaywrightApiClient(self.page)
        return self.client

    async def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """GET request."""
        client = self._get_client()
        return await client.get(endpoint, headers=headers)

    async def post(self, endpoint: str, data: Dict[str, Any],
                   headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """POST request."""
        client = self._get_client()
        return await client.post(endpoint, data=data, headers=headers)

    async def put(self, endpoint: str, data: Dict[str, Any],
                  headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """PUT request."""
        client = self._get_client()
        return await client.put(endpoint, data=data, headers=headers)

    async def patch(self, endpoint: str, data: Dict[str, Any],
                    headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """PATCH request."""
        client = self._get_client()
        return await client.patch(endpoint, data=data, headers=headers)

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """DELETE request."""
        client = self._get_client()
        return await client.delete(endpoint, headers=headers)
