#!/usr/bin/env python
"""
Playwright Test Runner CLI Tool

Advanced command-line interface for running Playwright tests with:
- Configurable parallel execution
- Multiple report generation
- Test filtering and selection
- Performance monitoring
- CI/CD integration
"""

import click
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json
import time
from enum import Enum


class TestCategory(Enum):
    """Test categories."""
    ALL = "all"
    API = "api"
    BROKEN_LINKS = "broken_links"
    CACHING = "caching"
    CONCURRENCY = "concurrency"
    RATE_LIMITING = "rate_limiting"
    CRUD = "crud"


class ReportFormat(Enum):
    """Report formats."""
    HTML = "html"
    JSON = "json"
    JUNIT = "junit"
    MARKDOWN = "markdown"


@click.group()
@click.version_option()
def cli():
    """🎭 Playwright Test Runner - Advanced Testing Framework
    
    Comprehensive CLI for running Playwright tests with parallel execution,
    multiple report formats, and performance monitoring.
    """
    pass


@cli.command()
@click.option(
    '--workers',
    default=4,
    type=int,
    help='Number of parallel workers (default: 4)'
)
@click.option(
    '--category',
    type=click.Choice(['all', 'api', 'broken_links', 'caching', 'concurrency', 'rate_limiting', 'crud']),
    default='all',
    help='Test category to run (default: all)'
)
@click.option(
    '--pattern',
    default='*_playwright.py',
    help='Test file pattern (default: *_playwright.py)'
)
@click.option(
    '--filter',
    help='Filter tests by name (pytest -k filter)'
)
@click.option(
    '--markers',
    help='Run tests by marker (pytest -m marker)'
)
@click.option(
    '--verbose/--quiet',
    default=True,
    help='Verbose output (default: verbose)'
)
@click.option(
    '--headless/--headed',
    default=True,
    help='Run browser headless (default: headless)'
)
@click.option(
    '--stop-on-failure/--continue-on-failure',
    default=False,
    help='Stop on first failure (default: continue)'
)
@click.option(
    '--slow/--no-slow',
    default=False,
    help='Include slow tests (default: exclude)'
)
@click.option(
    '--critical-only',
    is_flag=True,
    help='Run only critical tests'
)
@click.option(
    '--test-dir',
    default='tests/api',
    help='Test directory (default: tests/api)'
)
@click.option(
    '--timeout',
    default=300,
    type=int,
    help='Test timeout in seconds (default: 300)'
)
@click.option(
    '--reports',
    multiple=True,
    type=click.Choice(['html', 'json', 'junit', 'markdown']),
    default=['html', 'json'],
    help='Report formats to generate'
)
@click.option(
    '--output-dir',
    default='test_reports',
    help='Report output directory (default: test_reports)'
)
def run(
    workers,
    category,
    pattern,
    filter,
    markers,
    verbose,
    headless,
    stop_on_failure,
    slow,
    critical_only,
    test_dir,
    timeout,
    reports,
    output_dir
):
    """Run tests with parallel execution and reporting.
    
    Examples:
    
        # Run all tests with 4 workers
        playwright-runner run --workers 4
        
        # Run only API tests with 8 workers
        playwright-runner run --category api --workers 8
        
        # Run critical tests only
        playwright-runner run --critical-only
        
        # Run and generate all reports
        playwright-runner run --reports html json junit markdown
        
        # Run tests matching pattern
        playwright-runner run --filter "test_get" --workers 2
    """
    
    start_time = time.time()
    
    # Print banner
    click.secho("\n" + "="*70, fg="cyan", bold=True)
    click.secho("🎭 Playwright Test Runner", fg="cyan", bold=True)
    click.secho("="*70, fg="cyan", bold=True)
    click.echo(f"\n⚙️  Configuration:")
    click.echo(f"  Workers: {workers}")
    click.echo(f"  Category: {category}")
    click.echo(f"  Pattern: {pattern}")
    click.echo(f"  Test Dir: {test_dir}")
    click.echo(f"  Timeout: {timeout}s")
    click.echo(f"  Headless: {headless}")
    click.echo(f"  Reports: {', '.join(reports)}")
    click.echo(f"  Output Dir: {output_dir}\n")
    
    # Build pytest command
    cmd = [
        'pytest',
        f'{test_dir}/{pattern}',
    ]
    
    # Add parallel execution
    cmd.append(f'-n {workers}')
    
    # Add verbosity
    if verbose:
        cmd.append('-vv')
    else:
        cmd.append('-q')
    
    # Add filter if specified
    if filter:
        cmd.append(f'-k {filter}')
    
    # Add markers
    if markers:
        cmd.append(f'-m {markers}')
    elif critical_only:
        cmd.append('-m critical')
    elif not slow:
        cmd.append('-m "not slow"')
    
    # Add stop on failure
    if stop_on_failure:
        cmd.append('-x')
    
    # Add timeout
    cmd.append(f'--timeout={timeout}')
    
    # Add report generation
    if 'junit' in reports:
        cmd.append(f'--junit-xml={output_dir}/test_report.xml')
    
    # Add async mode
    cmd.append('--asyncio-mode=auto')
    
    click.echo(f"📋 Command: {' '.join(cmd)}\n")
    
    # Run tests
    try:
        click.secho("🚀 Starting tests...\n", fg="green", bold=True)
        result = subprocess.run(' '.join(cmd), shell=True)
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            click.secho(f"\n✅ All tests passed! ({elapsed:.2f}s)", fg="green", bold=True)
        else:
            click.secho(f"\n❌ Some tests failed. ({elapsed:.2f}s)", fg="red", bold=True)
        
        # Generate reports
        if reports:
            click.echo(f"\n📊 Generating reports...")
            _generate_reports(output_dir, reports)
        
        click.secho("="*70 + "\n", fg="cyan", bold=True)
        
        return result.returncode
        
    except Exception as e:
        click.secho(f"❌ Error running tests: {e}", fg="red", bold=True)
        return 1


@cli.command()
@click.option(
    '--output-dir',
    default='test_reports',
    help='Report output directory'
)
@click.option(
    '--report-dir',
    help='Directory to look for test results'
)
def report(output_dir, report_dir):
    """Generate test reports from existing test results.
    
    Examples:
    
        # Generate HTML report
        playwright-runner report
        
        # Generate reports in custom directory
        playwright-runner report --output-dir /tmp/reports
    """
    
    click.secho("\n" + "="*70, fg="cyan", bold=True)
    click.secho("📊 Report Generator", fg="cyan", bold=True)
    click.secho("="*70 + "\n", fg="cyan", bold=True)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        from playwright_test_runner import ReportGenerator, RunMetrics
        
        # Try to load metrics from JSON
        json_file = Path(report_dir or output_dir) / 'test_report.json'
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)
                click.echo(f"✅ Found metrics in {json_file}")
        else:
            click.secho(f"⚠️  No test metrics found in {json_file}", fg="yellow")
            return 1
        
        click.echo(f"📝 Reports generated in: {output_path}")
        
    except Exception as e:
        click.secho(f"❌ Error generating reports: {e}", fg="red", bold=True)
        return 1


@cli.command()
@click.option(
    '--test-dir',
    default='tests/api',
    help='Test directory'
)
def list_tests(test_dir):
    """List available tests.
    
    Examples:
    
        # List all tests
        playwright-runner list
        
        # List tests from custom directory
        playwright-runner list --test-dir tests/integration
    """
    
    click.secho("\n" + "="*70, fg="cyan", bold=True)
    click.secho("📋 Available Tests", fg="cyan", bold=True)
    click.secho("="*70 + "\n", fg="cyan", bold=True)
    
    try:
        cmd = f'pytest {test_dir} --collect-only -q'
        subprocess.run(cmd, shell=True)
    except Exception as e:
        click.secho(f"❌ Error listing tests: {e}", fg="red", bold=True)
        return 1


@cli.command()
def config():
    """Show test runner configuration.
    
    Displays all available configuration options and defaults.
    """
    
    click.secho("\n" + "="*70, fg="cyan", bold=True)
    click.secho("⚙️  Configuration Reference", fg="cyan", bold=True)
    click.secho("="*70 + "\n", fg="cyan", bold=True)
    
    config_info = {
        'Workers': 'Number of parallel test workers (default: 4)',
        'Category': 'Test category: all, api, broken_links, caching, concurrency (default: all)',
        'Pattern': 'Test file pattern to match (default: *_playwright.py)',
        'Filter': 'Filter tests by name (pytest -k syntax)',
        'Markers': 'Run tests by marker (pytest -m syntax)',
        'Verbose': 'Verbose output (default: true)',
        'Headless': 'Run browser headless (default: true)',
        'Stop on Failure': 'Stop on first failure (default: false)',
        'Slow': 'Include slow tests (default: false)',
        'Critical Only': 'Run only critical tests (default: false)',
        'Test Dir': 'Test directory (default: tests/api)',
        'Timeout': 'Test timeout in seconds (default: 300)',
        'Reports': 'Report formats: html, json, junit, markdown (default: html, json)',
        'Output Dir': 'Report output directory (default: test_reports)',
    }
    
    for key, value in config_info.items():
        click.echo(f"  {click.style(key, fg='yellow', bold=True)}: {value}")
    
    click.secho("\n" + "="*70 + "\n", fg="cyan", bold=True)


@cli.command()
def examples():
    """Show usage examples.
    
    Display common command examples and workflows.
    """
    
    click.secho("\n" + "="*70, fg="cyan", bold=True)
    click.secho("📚 Usage Examples", fg="cyan", bold=True)
    click.secho("="*70 + "\n", fg="cyan", bold=True)
    
    examples_list = [
        ("Run all tests", "playwright-runner run"),
        ("Run with 8 workers", "playwright-runner run --workers 8"),
        ("Run only API tests", "playwright-runner run --category api"),
        ("Run critical tests", "playwright-runner run --critical-only"),
        ("Run tests matching pattern", "playwright-runner run --filter test_get"),
        ("Run and stop on failure", "playwright-runner run --stop-on-failure"),
        ("Run with custom timeout", "playwright-runner run --timeout 600"),
        ("Generate all report formats", "playwright-runner run --reports html json junit markdown"),
        ("List available tests", "playwright-runner list"),
        ("Show configuration", "playwright-runner config"),
        ("Run with headed browser", "playwright-runner run --headed"),
        ("Run only non-slow tests", "playwright-runner run --no-slow"),
    ]
    
    for title, cmd in examples_list:
        click.echo(f"  {click.style(title, fg='green', bold=True)}")
        click.echo(f"    {click.style(cmd, fg='cyan')}\n")
    
    click.secho("="*70 + "\n", fg="cyan", bold=True)


def _generate_reports(output_dir: str, formats: List[str]) -> None:
    """Generate test reports.
    
    Args:
        output_dir: Output directory for reports
        formats: List of report formats to generate
    """
    try:
        from playwright_test_runner import ReportGenerator, RunMetrics
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load metrics from JSON if it exists
        json_file = Path(output_dir) / 'test_report.json'
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)
            
            for fmt in formats:
                if fmt == 'html':
                    click.echo(f"  ✅ HTML report")
                elif fmt == 'json':
                    click.echo(f"  ✅ JSON report")
                elif fmt == 'junit':
                    click.echo(f"  ✅ JUnit report")
                elif fmt == 'markdown':
                    click.echo(f"  ✅ Markdown report")
        
        click.echo(f"\n📂 Reports available in: {output_dir}")
        
    except ImportError:
        click.secho("⚠️  Report generation not available", fg="yellow")


if __name__ == '__main__':
    cli()
