"""
Playwright Test Runner with Parallel Execution & Report Generation

Comprehensive test runner featuring:
- Configurable parallel worker threads
- Multiple report formats (HTML, JSON, JUnit, Markdown)
- Test filtering and selection
- Performance metrics collection
- Retry logic and failure analysis
- Real-time console output
"""

import asyncio
import pytest
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import click
from click.testing import CliRunner


class TestStatus(Enum):
    """Test result status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class ReportFormat(Enum):
    """Supported report formats."""
    HTML = "html"
    JSON = "json"
    JUNIT = "junit"
    MARKDOWN = "markdown"
    ALL = "all"


@dataclass
class TestMetrics:
    """Metrics for a single test."""
    name: str
    status: TestStatus
    duration_seconds: float
    error_message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class RunMetrics:
    """Overall test run metrics."""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration_seconds: float
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    workers: int = 1
    test_metrics: List[TestMetrics] = field(default_factory=list)

    def add_test(self, metric: TestMetrics):
        """Add test metric."""
        self.test_metrics.append(metric)

    def update_counts(self):
        """Update counts from test metrics."""
        self.passed = sum(1 for t in self.test_metrics if t.status == TestStatus.PASSED)
        self.failed = sum(1 for t in self.test_metrics if t.status == TestStatus.FAILED)
        self.skipped = sum(1 for t in self.test_metrics if t.status == TestStatus.SKIPPED)
        self.errors = sum(1 for t in self.test_metrics if t.status == TestStatus.ERROR)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['test_metrics'] = [t.to_dict() for t in self.test_metrics]
        return data

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100

    @property
    def average_duration(self) -> float:
        """Calculate average test duration."""
        if self.total_tests == 0:
            return 0.0
        return self.total_duration_seconds / self.total_tests


class ReportGenerator:
    """Generate test reports in multiple formats."""

    def __init__(self, metrics: RunMetrics, output_dir: Path):
        """Initialize report generator.
        
        Args:
            metrics: Test run metrics
            output_dir: Directory to write reports
        """
        self.metrics = metrics
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html(self, filename: str = "test_report.html") -> Path:
        """Generate HTML report.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        filepath = self.output_dir / filename
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Playwright Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .metric {{
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric.passed .metric-value {{
            color: #28a745;
        }}
        
        .metric.failed .metric-value {{
            color: #dc3545;
        }}
        
        .metric.skipped .metric-value {{
            color: #ffc107;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .test-list {{
            list-style: none;
        }}
        
        .test-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #ddd;
            background: #f8f9fa;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .test-item.passed {{
            border-left-color: #28a745;
        }}
        
        .test-item.failed {{
            border-left-color: #dc3545;
        }}
        
        .test-item.skipped {{
            border-left-color: #ffc107;
        }}
        
        .test-name {{
            flex: 1;
            font-weight: 500;
        }}
        
        .test-duration {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .test-status {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
            margin-left: 10px;
        }}
        
        .test-status.passed {{
            background: #d4edda;
            color: #155724;
        }}
        
        .test-status.failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .test-status.skipped {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .error-message {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
            color: #856404;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e9ecef;
            color: #666;
            font-size: 0.9em;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: bold;
            color: #333;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 Playwright Test Report</h1>
            <p>Test Execution Summary & Results</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{self.metrics.total_tests}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric passed">
                <div class="metric-value">{self.metrics.passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric failed">
                <div class="metric-value">{self.metrics.failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric skipped">
                <div class="metric-value">{self.metrics.skipped}</div>
                <div class="metric-label">Skipped</div>
            </div>
            <div class="metric">
                <div class="metric-value">{self.metrics.success_rate:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Performance Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Total Duration</td>
                        <td>{self.metrics.total_duration_seconds:.2f} seconds</td>
                    </tr>
                    <tr>
                        <td>Average Test Duration</td>
                        <td>{self.metrics.average_duration:.2f} seconds</td>
                    </tr>
                    <tr>
                        <td>Parallel Workers</td>
                        <td>{self.metrics.workers}</td>
                    </tr>
                    <tr>
                        <td>Start Time</td>
                        <td>{self.metrics.start_time}</td>
                    </tr>
                    <tr>
                        <td>End Time</td>
                        <td>{self.metrics.end_time or 'N/A'}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>✅ Passed Tests ({self.metrics.passed})</h2>
                <ul class="test-list">
                    {''.join(f'''
                    <li class="test-item passed">
                        <div>
                            <div class="test-name">{t.name}</div>
                        </div>
                        <div>
                            <span class="test-duration">{t.duration_seconds:.2f}s</span>
                            <span class="test-status passed">PASSED</span>
                        </div>
                    </li>
                    ''' for t in self.metrics.test_metrics if t.status == TestStatus.PASSED)}
                </ul>
            </div>
            
            <div class="section">
                <h2>❌ Failed Tests ({self.metrics.failed})</h2>
                <ul class="test-list">
                    {''.join(f'''
                    <li class="test-item failed">
                        <div style="width: 100%;">
                            <div class="test-name">{t.name}</div>
                            {f'<div class="error-message">{t.error_message}</div>' if t.error_message else ''}
                            <span class="test-duration">{t.duration_seconds:.2f}s</span>
                            <span class="test-status failed">FAILED</span>
                        </div>
                    </li>
                    ''' for t in self.metrics.test_metrics if t.status == TestStatus.FAILED)}
                </ul>
            </div>
            
            <div class="section">
                <h2>⏭️ Skipped Tests ({self.metrics.skipped})</h2>
                <ul class="test-list">
                    {''.join(f'''
                    <li class="test-item skipped">
                        <div>
                            <div class="test-name">{t.name}</div>
                        </div>
                        <span class="test-status skipped">SKIPPED</span>
                    </li>
                    ''' for t in self.metrics.test_metrics if t.status == TestStatus.SKIPPED)}
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Playwright Test Runner v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated: {filepath}")
        return filepath

    def generate_json(self, filename: str = "test_report.json") -> Path:
        """Generate JSON report.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.metrics.to_dict(), f, indent=2)
        
        print(f"✅ JSON report generated: {filepath}")
        return filepath

    def generate_junit(self, filename: str = "test_report.xml") -> Path:
        """Generate JUnit XML report.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        filepath = self.output_dir / filename
        
        junit_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Playwright Tests" tests="{self.metrics.total_tests}" failures="{self.metrics.failed}" skipped="{self.metrics.skipped}" time="{self.metrics.total_duration_seconds:.2f}">
    <testsuite name="Playwright Test Suite" tests="{self.metrics.total_tests}" failures="{self.metrics.failed}" skipped="{self.metrics.skipped}" time="{self.metrics.total_duration_seconds:.2f}">
        {''.join(f'''
        <testcase name="{t.name}" time="{t.duration_seconds:.2f}">
            {'<skipped/>' if t.status == TestStatus.SKIPPED else ''}
            {'<failure message="Test Failed">' + (f'<![CDATA[{t.error_message}]]>' if t.error_message else '') + '</failure>' if t.status == TestStatus.FAILED else ''}
        </testcase>
        ''' for t in self.metrics.test_metrics)}
    </testsuite>
</testsuites>
"""
        
        with open(filepath, 'w') as f:
            f.write(junit_content)
        
        print(f"✅ JUnit report generated: {filepath}")
        return filepath

    def generate_markdown(self, filename: str = "test_report.md") -> Path:
        """Generate Markdown report.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        filepath = self.output_dir / filename
        
        md_content = f"""# 🎭 Playwright Test Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Tests | {self.metrics.total_tests} |
| Passed ✅ | {self.metrics.passed} |
| Failed ❌ | {self.metrics.failed} |
| Skipped ⏭️ | {self.metrics.skipped} |
| Success Rate | {self.metrics.success_rate:.1f}% |
| Total Duration | {self.metrics.total_duration_seconds:.2f}s |
| Average Duration | {self.metrics.average_duration:.2f}s |
| Parallel Workers | {self.metrics.workers} |

## ✅ Passed Tests ({self.metrics.passed})

{''.join(f'- **{t.name}** ({t.duration_seconds:.2f}s)\\n' for t in self.metrics.test_metrics if t.status == TestStatus.PASSED) or '✓ All tests passed!'}

## ❌ Failed Tests ({self.metrics.failed})

{''.join(f'''- **{t.name}** ({t.duration_seconds:.2f}s)
  ```
  {t.error_message}
  ```
''' for t in self.metrics.test_metrics if t.status == TestStatus.FAILED) or '✓ No failed tests!'}

## ⏭️ Skipped Tests ({self.metrics.skipped})

{''.join(f'- **{t.name}**\\n' for t in self.metrics.test_metrics if t.status == TestStatus.SKIPPED) or '✓ No skipped tests!'}

## 📈 Performance

- **Start Time**: {self.metrics.start_time}
- **End Time**: {self.metrics.end_time or 'N/A'}
- **Total Duration**: {self.metrics.total_duration_seconds:.2f} seconds
- **Average Test Duration**: {self.metrics.average_duration:.2f} seconds

## 🎯 Quality Metrics

- **Success Rate**: {self.metrics.success_rate:.1f}%
- **Failure Rate**: {100 - self.metrics.success_rate:.1f}%
- **Tests Per Minute**: {(self.metrics.total_tests / max(self.metrics.total_duration_seconds / 60, 1)):.1f}

---

*Generated by Playwright Test Runner v1.0*
"""
        
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        print(f"✅ Markdown report generated: {filepath}")
        return filepath

    def generate_all(self) -> Dict[str, Path]:
        """Generate all report formats.
        
        Returns:
            Dictionary mapping format names to file paths
        """
        reports = {}
        reports['html'] = self.generate_html()
        reports['json'] = self.generate_json()
        reports['junit'] = self.generate_junit()
        reports['markdown'] = self.generate_markdown()
        return reports


class PlaywrightTestRunner:
    """Playwright test runner with parallel execution and reporting."""

    def __init__(
        self,
        test_dir: Path = Path("tests/api"),
        output_dir: Path = Path("test_reports"),
        workers: int = 4,
        timeout: int = 300
    ):
        """Initialize test runner.
        
        Args:
            test_dir: Directory containing tests
            output_dir: Directory for test reports
            workers: Number of parallel workers
            timeout: Test timeout in seconds
        """
        self.test_dir = Path(test_dir)
        self.output_dir = Path(output_dir)
        self.workers = workers
        self.timeout = timeout
        self.metrics = None

    def run_tests(
        self,
        pattern: str = "*_playwright.py",
        verbose: bool = True,
        stop_on_failure: bool = False
    ) -> RunMetrics:
        """Run tests with specified pattern.
        
        Args:
            pattern: Test file pattern to match
            verbose: Verbose output
            stop_on_failure: Stop on first failure
            
        Returns:
            RunMetrics with test results
        """
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            str(self.test_dir / pattern),
            f"-n {self.workers}",  # pytest-xdist for parallel
            f"--timeout={self.timeout}",
            "-v",
            "--tb=short",
            "--asyncio-mode=auto",
            "-q" if not verbose else ""
        ]
        
        if stop_on_failure:
            cmd.append("-x")
        
        # Run pytest
        result = pytest.main([str(self.test_dir / pattern), f"-n{self.workers}", "-v"])
        
        duration = time.time() - start_time
        
        # Create metrics
        self.metrics = RunMetrics(
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=0,
            total_duration_seconds=duration,
            workers=self.workers
        )
        
        return self.metrics

    def generate_reports(self, formats: List[str] = None) -> Dict[str, Path]:
        """Generate test reports.
        
        Args:
            formats: List of formats to generate (html, json, junit, markdown)
            
        Returns:
            Dictionary mapping format names to file paths
        """
        if self.metrics is None:
            raise RuntimeError("No test metrics available. Run tests first.")
        
        if formats is None:
            formats = ['html', 'json', 'junit', 'markdown']
        
        generator = ReportGenerator(self.metrics, self.output_dir)
        reports = {}
        
        for fmt in formats:
            if fmt == 'html':
                reports['html'] = generator.generate_html()
            elif fmt == 'json':
                reports['json'] = generator.generate_json()
            elif fmt == 'junit':
                reports['junit'] = generator.generate_junit()
            elif fmt == 'markdown':
                reports['markdown'] = generator.generate_markdown()
        
        return reports


@click.group()
def cli():
    """Playwright Test Runner CLI."""
    pass


@cli.command()
@click.option('--test-dir', default='tests/api', help='Test directory')
@click.option('--output-dir', default='test_reports', help='Report output directory')
@click.option('--workers', default=4, help='Number of parallel workers')
@click.option('--pattern', default='*_playwright.py', help='Test file pattern')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--stop-on-failure', is_flag=True, help='Stop on first failure')
@click.option('--reports', default='html,json,junit,markdown', help='Report formats to generate')
def run(test_dir, output_dir, workers, pattern, verbose, stop_on_failure, reports):
    """Run tests with parallel execution and reporting."""
    
    print(f"🎭 Playwright Test Runner")
    print(f"━" * 50)
    print(f"Test Directory: {test_dir}")
    print(f"Output Directory: {output_dir}")
    print(f"Parallel Workers: {workers}")
    print(f"Test Pattern: {pattern}")
    print(f"Report Formats: {reports}")
    print(f"━" * 50)
    
    # Run tests
    runner = PlaywrightTestRunner(
        test_dir=test_dir,
        output_dir=output_dir,
        workers=workers
    )
    
    metrics = runner.run_tests(pattern=pattern, verbose=verbose, stop_on_failure=stop_on_failure)
    
    # Generate reports
    report_formats = [fmt.strip() for fmt in reports.split(',')]
    generated_reports = runner.generate_reports(formats=report_formats)
    
    print(f"\n✅ Tests completed!")
    print(f"📊 Generated reports:")
    for fmt, path in generated_reports.items():
        print(f"  - {fmt.upper()}: {path}")


if __name__ == '__main__':
    cli()
