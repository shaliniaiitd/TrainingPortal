"""
Test Configuration File for TrainingPortal

Central configuration for all test execution including:
- Base URLs (API, Web)
- Parallel execution settings
- Report generation options
- Browser & environment settings
- Test filters and markers
- Logging configuration
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class TestEnvironment(Enum):
    """Test execution environment."""
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class ReportFormat(Enum):
    """Supported report formats."""
    HTML = "html"
    JSON = "json"
    ALLURE = "allure"
    MARKDOWN = "markdown"


class ParallelStrategy(Enum):
    """Parallel execution strategy."""
    PYTEST_XDIST = "pytest_xdist"  # pytest-xdist (traditional)
    PLAYWRIGHT_NATIVE = "playwright"  # Playwright's native approach


@dataclass
class URLConfig:
    """URL Configuration."""

    # Local development
    base_url: str = "http://127.0.0.1:8000/"
    api_base_url: str = "http://127.0.0.1:8000/myapp/api"
    web_url: str = "http://127.0.0.1:8000/myapp"

    # Staging (optional)
    staging_base_url: str = "https://staging.example.com"
    staging_api_url: str = "https://staging.example.com/api"

    # Production (optional)
    prod_base_url: str = "https://api.example.com"
    prod_api_url: str = "https://api.example.com/api"


@dataclass
class BrowserConfig:
    """Browser Configuration."""

    # Browser settings
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    slow_motion: int = 0  # milliseconds
    timeout: int = 30000  # milliseconds (30 seconds)

    # Launch arguments
    ignore_https_errors: bool = True
    args: List[str] = None

    def __post_init__(self):
        if self.args is None:
            self.args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]


@dataclass
class ParallelConfig:
    """Parallel Execution Configuration."""

    # Parallel strategy
    strategy: ParallelStrategy = ParallelStrategy.PYTEST_XDIST

    # Worker configuration
    workers: int = 4  # Number of parallel workers
    max_workers: int = 16
    min_workers: int = 1

    # Timeout settings
    test_timeout: int = 300  # seconds
    global_timeout: int = 3600  # seconds (1 hour)

    # Retry settings
    retry_count: int = 2
    retry_on_failure: bool = True

    # Distribution
    auto_detect_workers: bool = True  # Auto-detect optimal worker count


@dataclass
class ReportConfig:
    """Report Generation Configuration."""

    # Report formats
    formats: List[ReportFormat] = None
    output_dir: str = "test_reports"

    # Allure settings
    allure_enabled: bool = True
    allure_dir: str = "allure-results"

    # HTML report settings
    html_enabled: bool = True
    html_self_contained: bool = True

    # JSON report settings
    json_enabled: bool = True

    # Markdown settings
    markdown_enabled: bool = True

    # Store detailed logs
    store_logs: bool = True
    logs_dir: str = "test_logs"

    def __post_init__(self):
        if self.formats is None:
            self.formats = [
                ReportFormat.ALLURE,
                ReportFormat.HTML,
                ReportFormat.JSON,
                ReportFormat.MARKDOWN
            ]


@dataclass
class LoggingConfig:
    """Logging Configuration."""

    # Log level
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Log files
    log_file: str = "test_execution.log"
    detailed_log_file: str = "test_execution_detailed.log"

    # Console output
    console_output: bool = True
    console_level: str = "INFO"

    # Capture settings
    capture_stdout: bool = True
    capture_stderr: bool = True
    capture_logs: bool = True


@dataclass
class TestConfig:
    """Master Test Configuration."""

    # Environment
    environment: TestEnvironment = TestEnvironment.LOCAL

    # URLs
    urls: URLConfig = None

    # Browser settings
    browser: BrowserConfig = None

    # Parallel execution
    parallel: ParallelConfig = None

    # Reporting
    reporting: ReportConfig = None

    # Logging
    logging: LoggingConfig = None

    # Test markers (which tests to run)
    markers: List[str] = None

    # Test filters (by name pattern)
    filters: List[str] = None

    # Include slow tests
    include_slow: bool = False

    # Stop on first failure
    stop_on_failure: bool = False

    # Verbose output
    verbose: bool = True

    # Debug mode
    debug: bool = False

    def __post_init__(self):
        if self.urls is None:
            self.urls = URLConfig()
        if self.browser is None:
            self.browser = BrowserConfig()
        if self.parallel is None:
            self.parallel = ParallelConfig()
        if self.reporting is None:
            self.reporting = ReportConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.markers is None:
            self.markers = []
        if self.filters is None:
            self.filters = []


# Default configuration instance
DEFAULT_CONFIG = TestConfig()


# Preset configurations for common scenarios
class Presets:
    """Common configuration presets."""

    @staticmethod
    def fast_local() -> TestConfig:
        """Fast local testing with minimal overhead."""
        return TestConfig(
            environment=TestEnvironment.LOCAL,
            parallel=ParallelConfig(workers=4, test_timeout=60),
            browser=BrowserConfig(headless=True),
            reporting=ReportConfig(formats=[ReportFormat.ALLURE, ReportFormat.HTML]),
            markers=['critical'],
            include_slow=False
        )

    @staticmethod
    def full_local() -> TestConfig:
        """Full local testing with all tests."""
        return TestConfig(
            environment=TestEnvironment.LOCAL,
            parallel=ParallelConfig(workers=4, test_timeout=300),
            browser=BrowserConfig(headless=True),
            reporting=ReportConfig(formats=[
                ReportFormat.ALLURE,
                ReportFormat.HTML,
                ReportFormat.JSON,
                ReportFormat.MARKDOWN
            ]),
            include_slow=True,
            verbose=True
        )

    @staticmethod
    def ci_pipeline() -> TestConfig:
        """CI/CD pipeline configuration."""
        return TestConfig(
            environment=TestEnvironment.STAGING,
            parallel=ParallelConfig(
                workers=8,
                test_timeout=300,
                retry_count=1
            ),
            browser=BrowserConfig(headless=True),
            reporting=ReportConfig(formats=[
                ReportFormat.ALLURE,
                ReportFormat.JSON
            ]),
            stop_on_failure=False,
            verbose=False
        )

    @staticmethod
    def debug() -> TestConfig:
        """Debug configuration with headed browser."""
        return TestConfig(
            environment=TestEnvironment.LOCAL,
            parallel=ParallelConfig(workers=1, test_timeout=600),
            browser=BrowserConfig(headless=False, slow_motion=500),
            reporting=ReportConfig(formats=[ReportFormat.HTML]),
            debug=True,
            verbose=True
        )

    @staticmethod
    def performance() -> TestConfig:
        """Performance testing configuration."""
        return TestConfig(
            environment=TestEnvironment.LOCAL,
            parallel=ParallelConfig(
                workers=16,
                auto_detect_workers=True,
                test_timeout=600
            ),
            browser=BrowserConfig(headless=True),
            reporting=ReportConfig(formats=[ReportFormat.JSON]),
            include_slow=True
        )


# Configuration examples for different use cases
CONFIG_EXAMPLES = {
    'fast': Presets.fast_local(),
    'full': Presets.full_local(),
    'ci': Presets.ci_pipeline(),
    'debug': Presets.debug(),
    'performance': Presets.performance(),
}

if __name__ == '__main__':
    # Print configuration for verification
    print("🎭 Test Configuration")
    print(f"\nDefault Configuration:")
    print(f"  Base URL: {DEFAULT_CONFIG.urls.base_url}")
    print(f"  API Base URL: {DEFAULT_CONFIG.urls.api_base_url}")
    print(f"  Web URL: {DEFAULT_CONFIG.urls.web_url}")
    print(f"  Workers: {DEFAULT_CONFIG.parallel.workers}")
    print(f"  Report Formats: {', '.join(f.value for f in DEFAULT_CONFIG.reporting.formats)}")
    print(f"  Browser: {DEFAULT_CONFIG.browser.browser_type}")
    print(f"  Headless: {DEFAULT_CONFIG.browser.headless}")
    print(f"\nAvailable Presets:")
    for name in CONFIG_EXAMPLES.keys():
        print(f"  • {name}")
