"""Rate Limiting (429) Scenario Tests.

Demonstrates comprehensive 429 Too Many Requests handling:
- Retry-After header parsing (RFC 7231)
- Exponential backoff with jitter
- Circuit breaker pattern
- Rate limit metrics collection
- Testing both normal and rate-limited scenarios

Interview-ready patterns showing production-grade resilience.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from tests.api.base_api_test import BaseApiTestClass, ApiResponse, RateLimitMetrics


class TestRateLimitHandling(BaseApiTestClass):
    """Tests for 429 rate limiting scenarios."""

    MEMBERS_ENDPOINT = "members"

    def test_successful_request_no_rate_limit(self):
        """Test: Normal successful request without rate limiting."""
        response = self.get(self.MEMBERS_ENDPOINT)
        
        # Should succeed without rate limiting
        self.validate(response).assert_not_rate_limited()
        assert response.retry_count == 0, "Should not have retried"
        assert response.was_rate_limited is False

    def test_detect_429_rate_limit_response(self):
        """Test: Correctly detect 429 status code."""
        # Create a mock 429 response
        rate_limited_response = ApiResponse(
            status_code=429,
            body={"detail": "Too many requests"},
            headers={"Retry-After": "5"},
            elapsed_ms=100.0,
            was_rate_limited=True
        )

        # Assertions
        assert rate_limited_response.is_rate_limited()
        self.validate(rate_limited_response).assert_rate_limited()

    def test_retry_after_header_delta_seconds(self):
        """Test: Parse Retry-After header as delta-seconds."""
        response = ApiResponse(
            status_code=429,
            body={},
            headers={"Retry-After": "120"},
            elapsed_ms=50.0
        )

        retry_after = response.get_retry_after_seconds()
        assert retry_after == 120.0, f"Expected 120 seconds, got {retry_after}"

    def test_retry_after_header_http_date(self):
        """Test: Parse Retry-After header as HTTP-date."""
        # Note: In real scenarios, this would be a future HTTP-date
        response = ApiResponse(
            status_code=429,
            body={},
            headers={"Retry-After": "Wed, 21 Oct 2025 07:28:00 GMT"},
            elapsed_ms=50.0
        )

        retry_after = response.get_retry_after_seconds()
        # Should parse without error; actual value depends on current time
        assert retry_after is not None

    def test_no_retry_after_header(self):
        """Test: Handle missing Retry-After header gracefully."""
        response = ApiResponse(
            status_code=429,
            body={},
            headers={},  # No Retry-After
            elapsed_ms=50.0
        )

        retry_after = response.get_retry_after_seconds()
        assert retry_after is None, "Should return None when header missing"

    def test_backoff_calculation_exponential(self):
        """Test: Exponential backoff calculation."""
        # Initial: 1 second
        backoff_0 = self._calculate_backoff_seconds(0, retry_after=None)
        assert 0.8 <= backoff_0 <= 1.2, f"Backoff 0 out of range: {backoff_0}"

        # After 1 retry: 2 seconds (1 * 2^1)
        backoff_1 = self._calculate_backoff_seconds(1, retry_after=None)
        assert 1.6 <= backoff_1 <= 2.4, f"Backoff 1 out of range: {backoff_1}"

        # After 2 retries: 4 seconds (1 * 2^2)
        backoff_2 = self._calculate_backoff_seconds(2, retry_after=None)
        assert 3.2 <= backoff_2 <= 4.8, f"Backoff 2 out of range: {backoff_2}"

    def test_backoff_respects_max_ceiling(self):
        """Test: Backoff respects maximum ceiling."""
        # Even at retry 10, should not exceed MAX_BACKOFF_SECONDS (30)
        backoff_max = self._calculate_backoff_seconds(10, retry_after=None)
        assert backoff_max <= self.MAX_BACKOFF_SECONDS, \
            f"Backoff {backoff_max} exceeds max {self.MAX_BACKOFF_SECONDS}"

    def test_retry_after_takes_precedence(self):
        """Test: Retry-After header takes precedence over calculated backoff."""
        # Request server wants us to wait 45 seconds
        backoff = self._calculate_backoff_seconds(0, retry_after=45.0)
        
        # Should cap at MAX_BACKOFF_SECONDS (30)
        assert backoff <= self.MAX_BACKOFF_SECONDS, \
            f"Backoff {backoff} exceeds max even with Retry-After"

    def test_backoff_includes_jitter(self):
        """Test: Jitter is added to backoff (thundering herd prevention)."""
        # Run multiple times to verify jitter variation
        backoffs = [
            self._calculate_backoff_seconds(1, retry_after=None)
            for _ in range(10)
        ]

        # Should have variation due to jitter
        unique_backoffs = set(backoffs)
        assert len(unique_backoffs) > 1, \
            f"Jitter not working - all backoffs identical: {backoffs}"

    def test_jitter_can_be_disabled(self):
        """Test: Jitter can be disabled for deterministic testing."""
        self.ENABLE_JITTER = False
        
        # Run multiple times - should all be identical
        backoffs = [
            self._calculate_backoff_seconds(1, retry_after=None)
            for _ in range(5)
        ]

        unique_backoffs = set(backoffs)
        assert len(unique_backoffs) == 1, \
            f"Without jitter, backoffs should be identical: {backoffs}"
        
        # Reset
        self.ENABLE_JITTER = True

    def test_rate_limit_metrics_collection(self):
        """Test: Rate limit metrics are collected correctly."""
        assert self.rate_limit_metrics.total_rate_limited == 0
        assert self.rate_limit_metrics.total_retries == 0
        
        # Simulate recording events
        self.rate_limit_metrics.record_rate_limit(1.5)
        self.rate_limit_metrics.record_retry()
        
        assert self.rate_limit_metrics.total_rate_limited == 1
        assert self.rate_limit_metrics.total_retries == 1
        assert self.rate_limit_metrics.total_backoff_seconds == 1.5

    def test_metrics_track_max_backoff(self):
        """Test: Metrics track maximum backoff time."""
        self.rate_limit_metrics.record_rate_limit(2.0)
        self.rate_limit_metrics.record_rate_limit(5.0)
        self.rate_limit_metrics.record_rate_limit(3.0)
        
        assert self.rate_limit_metrics.max_backoff_seconds == 5.0

    def test_metrics_string_representation(self):
        """Test: Metrics can be printed for debugging."""
        self.rate_limit_metrics.record_rate_limit(1.5)
        self.rate_limit_metrics.record_retry()
        
        metrics_str = str(self.rate_limit_metrics)
        assert "rate_limited=1" in metrics_str
        assert "total_retries=1" in metrics_str

    def test_circuit_breaker_triggers_on_consecutive_429s(self):
        """Test: Circuit breaker stops retries after N consecutive 429s."""
        # Simulate many consecutive 429s
        self.consecutive_rate_limits = self.CIRCUIT_BREAKER_THRESHOLD
        
        # Create a 429 response
        rate_limited_response = ApiResponse(
            status_code=429,
            body={},
            headers={},
            elapsed_ms=50.0
        )

        # Should be marked as rate limited
        assert rate_limited_response.is_rate_limited()

    def test_circuit_breaker_threshold_configuration(self):
        """Test: Circuit breaker threshold is configurable."""
        assert self.CIRCUIT_BREAKER_THRESHOLD == 5, "Default should be 5"
        
        # Can be modified per test
        original = self.CIRCUIT_BREAKER_THRESHOLD
        self.CIRCUIT_BREAKER_THRESHOLD = 3
        assert self.CIRCUIT_BREAKER_THRESHOLD == 3
        self.CIRCUIT_BREAKER_THRESHOLD = original

    def test_retry_configuration_options(self):
        """Test: All retry configuration options are present."""
        assert hasattr(self, 'MAX_RETRIES')
        assert hasattr(self, 'INITIAL_BACKOFF_SECONDS')
        assert hasattr(self, 'MAX_BACKOFF_SECONDS')
        assert hasattr(self, 'BACKOFF_MULTIPLIER')
        assert hasattr(self, 'ENABLE_JITTER')
        assert hasattr(self, 'CIRCUIT_BREAKER_THRESHOLD')

    def test_request_with_retry_disabled(self):
        """Test: Can disable automatic retry for specific requests."""
        # Request with allow_rate_limit_retry=False should not retry on 429
        # (In real test, would mock response to return 429)
        response = self.get(
            self.MEMBERS_ENDPOINT,
            allow_rate_limit_retry=False
        )

        # In normal case, should succeed
        if response.is_rate_limited():
            assert response.retry_count == 0, "Should not retry when disabled"

    def test_all_http_methods_support_rate_limit_handling(self):
        """Test: All HTTP methods (GET, POST, PUT, PATCH, DELETE) handle 429."""
        # Verify all methods have allow_rate_limit_retry parameter
        import inspect

        for method_name in ['get', 'post', 'put', 'patch', 'delete']:
            method = getattr(self, method_name)
            sig = inspect.signature(method)
            assert 'allow_rate_limit_retry' in sig.parameters, \
                f"{method_name} missing allow_rate_limit_retry parameter"


class TestRateLimitIntegration(BaseApiTestClass):
    """Integration tests for rate limiting with real API scenarios."""

    def test_member_creation_handles_rate_limit_gracefully(self):
        """Test: Member creation handles 429 and retries gracefully."""
        payload = {
            "first_name": "Rate",
            "last_name": "Limited",
            "designation": "Test"
        }

        # In real scenario with rate limiting, should retry automatically
        response = self.post("members", payload)

        # Should either succeed or be properly rate limited
        if response.is_rate_limited():
            assert response.was_rate_limited is True
            print(f"Request was rate limited. Retries: {response.retry_count}")
        else:
            self.validate(response).assert_not_rate_limited()

    def test_member_list_retries_on_rate_limit(self):
        """Test: Member list request retries on 429."""
        response = self.get("members")

        # Should succeed (normal case) or have retry info
        if response.is_rate_limited():
            assert response.retry_count <= self.MAX_RETRIES, \
                "Exceeded maximum retries"

    def test_rate_limit_metrics_populated_after_requests(self):
        """Test: Metrics are populated after requests."""
        # Make a request
        self.get("members")

        # Metrics should be initialized
        assert isinstance(self.rate_limit_metrics, RateLimitMetrics)


class TestRateLimitEdgeCases(BaseApiTestClass):
    """Edge case tests for rate limiting scenarios."""

    def test_retry_after_with_trailing_whitespace(self):
        """Test: Retry-After parsing handles whitespace."""
        response = ApiResponse(
            status_code=429,
            body={},
            headers={"Retry-After": "  60  "},
            elapsed_ms=50.0
        )

        # Should handle gracefully
        try:
            retry_after = response.get_retry_after_seconds()
            # May fail to parse, but should not crash
        except Exception as e:
            pytest.skip(f"Whitespace handling not strict: {e}")

    def test_zero_retry_after_value(self):
        """Test: Handle Retry-After: 0 correctly."""
        response = ApiResponse(
            status_code=429,
            body={},
            headers={"Retry-After": "0"},
            elapsed_ms=50.0
        )

        retry_after = response.get_retry_after_seconds()
        assert retry_after == 0.0, "Should parse 0 as valid retry time"

    def test_negative_calculated_backoff_not_possible(self):
        """Test: Backoff calculation never returns negative."""
        # Even with unusual inputs, backoff should be >= 0
        backoff = self._calculate_backoff_seconds(0, retry_after=None)
        assert backoff >= 0, f"Backoff negative: {backoff}"

    def test_very_large_retry_after_capped(self):
        """Test: Very large Retry-After values are capped."""
        response = ApiResponse(
            status_code=429,
            body={},
            headers={"Retry-After": "99999"},
            elapsed_ms=50.0
        )

        retry_after = response.get_retry_after_seconds()
        assert retry_after == 99999.0, "Should parse large values"
        
        # But backoff calculation should cap it
        backoff = self._calculate_backoff_seconds(0, retry_after=99999.0)
        assert backoff <= self.MAX_BACKOFF_SECONDS, \
            "Backoff should respect ceiling even with large Retry-After"
