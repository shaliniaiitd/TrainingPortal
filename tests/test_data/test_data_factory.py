"""
Test Data Factory
Factory pattern for creating appropriate data providers based on source type.
"""

from typing import Optional, Dict, Union
from test_data_provider import (
    TestDataProvider,
    ExcelTestDataProvider,
    JSONTestDataProvider,
    DBTestDataProvider,
    DataSourceType,
)
import os


class TestDataFactory:
    """
    Factory for creating test data providers.
    Auto-detects provider type based on file extension or explicit specification.
    """

    @staticmethod
    def create_provider(
        source: str,
        provider_type: Optional[DataSourceType] = None,
        **kwargs
    ) -> TestDataProvider:
        """
        Create and return appropriate data provider.

        Args:
            source: Source path or connection string
            provider_type: Explicit provider type. If None, auto-detects from source.
            **kwargs: Additional arguments for specific providers

        Returns:
            TestDataProvider instance

        Raises:
            ValueError: If provider type cannot be determined or is unsupported

        Examples:
            # Auto-detect from file extension
            provider = TestDataFactory.create_provider("tests/data/test_data.xlsx")

            # Explicit provider type
            provider = TestDataFactory.create_provider(
                "tests/data/test_data.json",
                provider_type=DataSourceType.JSON
            )

            # Database provider
            provider = TestDataFactory.create_provider(
                "sqlite:///test_data.db",
                provider_type=DataSourceType.DATABASE,
                tables={"Members": "members_data"}
            )
        """
        # Determine provider type
        if provider_type is None:
            provider_type = TestDataFactory._detect_provider_type(source)

        # Create and return appropriate provider
        if provider_type == DataSourceType.EXCEL:
            return ExcelTestDataProvider(source)

        elif provider_type == DataSourceType.JSON:
            return JSONTestDataProvider(source)

        elif provider_type == DataSourceType.DATABASE:
            tables = kwargs.get("tables")
            return DBTestDataProvider(source, tables=tables)

        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    @staticmethod
    def _detect_provider_type(source: str) -> DataSourceType:
        """
        Auto-detect provider type from source.

        Args:
            source: Source path or connection string

        Returns:
            DataSourceType enum value
        """
        # Database connection strings
        if any(source.startswith(prefix) for prefix in ["sqlite://", "postgresql://", "mysql://", "mysql+pymysql://"]):
            return DataSourceType.DATABASE

        # File-based sources
        if isinstance(source, str):
            _, ext = os.path.splitext(source)

            if ext.lower() == ".xlsx":
                return DataSourceType.EXCEL
            elif ext.lower() == ".json":
                return DataSourceType.JSON

        raise ValueError(
            f"Cannot determine provider type for source: {source}\n"
            f"Specify provider_type explicitly using DataSourceType enum"
        )

    @staticmethod
    def create_from_env() -> TestDataProvider:
        """
        Create provider from environment variable.
        Expects environment variable 'TEST_DATA_SOURCE' with data source path/connection string.

        Returns:
            TestDataProvider instance

        Raises:
            ValueError: If TEST_DATA_SOURCE environment variable not set
        """
        source = os.getenv("TEST_DATA_SOURCE")
        if not source:
            raise ValueError(
                "TEST_DATA_SOURCE environment variable not set.\n"
                "Set it to point to your test data source (file or database)."
            )

        return TestDataFactory.create_provider(source)
