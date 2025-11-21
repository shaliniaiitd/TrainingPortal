"""
Pytest configuration for test data providers.
Provides fixtures for different provider types using the factory pattern.

This file should be at tests/ level so pytest can discover it automatically.
"""

import pytest
import os
import sys

# Add test_data directory to path to import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "test_data"))

from test_data_factory import TestDataFactory, DataSourceType


@pytest.fixture(scope="session")
def test_data_provider():
    """
    Fixture: Provide test data provider for the entire session.
    Auto-detects provider type from default test data source.
    """
    # Try multiple sources in order of preference
    sources = [
        ("tests/test_data/test_data.xlsx", DataSourceType.EXCEL),
        ("tests/test_data/test_data.json", DataSourceType.JSON),
        ("sqlite:///tests/test_data/test_data.db", DataSourceType.DATABASE),
    ]

    provider = None
    for source, provider_type in sources:
        try:
            if provider_type == DataSourceType.DATABASE or os.path.exists(source):
                provider = TestDataFactory.create_provider(
                    source,
                    provider_type=provider_type
                )
                provider.print_summary()
                break
        except Exception as e:
            continue

    if provider is None:
        raise RuntimeError(
            "No test data source found. Generate with: python tests/test_data/generate_test_data.py"
        )

    yield provider

    # Cleanup
    if hasattr(provider, 'close'):
        provider.close()


@pytest.fixture
def member_data(test_data_provider):
    """Fixture: Get next member test data."""
    test_data_provider.reset_index("Members")
    return test_data_provider.get_next_data("Members")


@pytest.fixture
def course_data(test_data_provider):
    """Fixture: Get next course test data."""
    test_data_provider.reset_index("Courses")
    return test_data_provider.get_next_data("Courses")


@pytest.fixture
def student_data(test_data_provider):
    """Fixture: Get next student test data."""
    test_data_provider.reset_index("Students")
    return test_data_provider.get_next_data("Students")


@pytest.fixture
def all_members_data(test_data_provider):
    """Fixture: Get all members test data."""
    return test_data_provider.get_members_data()


@pytest.fixture
def all_courses_data(test_data_provider):
    """Fixture: Get all courses test data."""
    return test_data_provider.get_courses_data()


@pytest.fixture
def all_students_data(test_data_provider):
    """Fixture: Get all students test data."""
    return test_data_provider.get_students_data()


# Convenience fixtures using factory
@pytest.fixture
def excel_provider():
    """Fixture: Provide Excel test data provider."""
    return TestDataFactory.create_provider("tests/test_data/test_data.xlsx")


@pytest.fixture
def json_provider():
    """Fixture: Provide JSON test data provider."""
    return TestDataFactory.create_provider("tests/test_data/test_data.json")


@pytest.fixture
def db_provider():
    """Fixture: Provide Database test data provider."""
    return TestDataFactory.create_provider("sqlite:///tests/test_data/test_data.db")
