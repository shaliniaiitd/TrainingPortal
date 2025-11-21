# Test Data Provider Architecture

Extensible, pluggable test data management system supporting Excel, JSON, and Database sources.

## Architecture Overview

### Class Hierarchy

```
TestDataProvider (Abstract Base Class)
├── ExcelTestDataProvider
├── JSONTestDataProvider
└── DBTestDataProvider
```

### Core Components

1. **TestDataProvider**: Abstract base class defining interface
2. **ExcelTestDataProvider**: Implementation for Excel files (.xlsx)
3. **JSONTestDataProvider**: Implementation for JSON files (.json)
4. **DBTestDataProvider**: Implementation for SQL databases
5. **TestDataFactory**: Factory for creating appropriate providers
6. **TestDataGenerator**: Generate test data in multiple formats

## Quick Start

### 1. Generate Test Data

```bash
cd tests/data
python generate_test_data.py
```

Generates test data in all available formats:
- `test_data.xlsx` (Excel)
- `test_data.json` (JSON)
- `test_data.db` (SQLite)

### 2. Use in Tests

#### Using Fixtures (Recommended)

```python
def test_add_member(member_data):
    """Automatically loads from default source"""
    first_name = member_data["first_name"]
    last_name = member_data["last_name"]
```

#### Using Factory Directly

```python
from test_data_factory import TestDataFactory

def test_something():
    provider = TestDataFactory.create_provider("tests/data/test_data.xlsx")
    members = provider.get_all_data("Members")
```

#### Using Specific Provider

```python
from test_data_provider import ExcelTestDataProvider

def test_something():
    provider = ExcelTestDataProvider("tests/data/test_data.xlsx")
    member = provider.get_next_data("Members")
```

## API Reference

### TestDataProvider (Base Class)

#### Core Methods

```python
load()                                      # Load data from source
get_all_data(sheet_name) -> List[Dict]     # Get all rows
get_next_data(sheet_name) -> Dict          # Get next row sequentially
get_by_id(sheet_name, id) -> Dict          # Get specific row by ID
get_by_name(sheet_name, name) -> Dict      # Get specific row by name
get_by_field(sheet_name, field, value)     # Get rows matching field
get_by_filter(sheet_name, **filters)       # Get rows with multiple filters
get_random_data(sheet_name) -> Dict        # Get random row
reset_index(sheet_name=None)                # Reset sequential index
get_sheet_names() -> List[str]              # List available sheets
get_row_count(sheet_name) -> int            # Count rows
print_summary()                             # Print data summary
```

#### Convenience Methods

```python
get_members_data()      # Get all members
get_courses_data()      # Get all courses
get_students_data()     # Get all students
get_next_member()       # Get next member
get_next_course()       # Get next course
get_next_student()      # Get next student
```

### TestDataFactory

```python
# Auto-detect provider type
provider = TestDataFactory.create_provider("tests/data/test_data.xlsx")

# Explicit provider type
provider = TestDataFactory.create_provider(
    "sqlite:///test.db",
    provider_type=DataSourceType.DATABASE,
    tables={"Members": "members_data"}
)

# From environment variable
provider = TestDataFactory.create_from_env()  # Uses TEST_DATA_SOURCE env var
```

### ExcelTestDataProvider

```python
provider = ExcelTestDataProvider("tests/data/test_data.xlsx")
data = provider.get_all_data("Members")
```

**Requirements**: `pip install openpyxl`

### JSONTestDataProvider

```python
provider = JSONTestDataProvider("tests/data/test_data.json")
data = provider.get_all_data("Members")
```

No external dependencies.

### DBTestDataProvider

```python
provider = DBTestDataProvider(
    "sqlite:///test.db",
    tables={"Members": "members", "Courses": "courses"}
)
data = provider.get_all_data("Members")
provider.close()  # Don't forget to close!
```

**Requirements**: `pip install sqlalchemy`

**Supported Databases**:
- SQLite: `sqlite:///path/to/db.db`
- PostgreSQL: `postgresql://user:pass@localhost/db`
- MySQL: `mysql+pymysql://user:pass@localhost/db`

## Usage Examples

### Example 1: Happy Path Test with Auto-detected Provider

```python
def test_add_member(page, member_data):
    """
    member_data is automatically loaded from configured source.
    Provider type auto-detected from file extension.
    """
    add_member = AddMemberPage(page)
    add_member.fill_form(
        member_data["first_name"],
        member_data["last_name"],
        member_data["designation"]
    )
    add_member.submit()
```

### Example 2: Filter Test Data by Type

```python
def test_with_happy_path_data(test_data_provider):
    """Get only happy_path test data"""
    members = test_data_provider.get_by_filter(
        "Members",
        test_type="happy_path"
    )
    
    for member in members:
        # Test each happy path member
        pass
```

### Example 3: Switch Between Providers

```python
import os

def test_with_different_sources():
    """Test with different data sources"""
    
    # Use Excel
    excel_provider = TestDataFactory.create_provider("tests/data/test_data.xlsx")
    excel_data = excel_provider.get_members_data()
    
    # Use JSON
    json_provider = TestDataFactory.create_provider("tests/data/test_data.json")
    json_data = json_provider.get_members_data()
    
    # Use Database
    db_provider = TestDataFactory.create_provider("sqlite:///test.db")
    db_data = db_provider.get_members_data()
    db_provider.close()
    
    # All should have same data structure
    assert excel_data[0].keys() == json_data[0].keys()
```

### Example 4: Sequential Data Access

```python
def test_sequential_members(test_data_provider):
    """Get members one by one"""
    test_data_provider.reset_index("Members")
    
    member1 = test_data_provider.get_next_data("Members")
    member2 = test_data_provider.get_next_data("Members")
    member3 = test_data_provider.get_next_data("Members")
    
    # After reaching end, cycles back to start
    member1_again = test_data_provider.get_next_data("Members")
```

### Example 5: Random Data Selection

```python
def test_with_random_member(test_data_provider):
    """Get random member for each test run"""
    random_member = test_data_provider.get_random_data("Members")
    
    # Use random member for testing
    members_page.member_exists(random_member["first_name"])
```

## Installation

### Core (all providers)
```bash
pip install -e .
```

### Excel support
```bash
pip install openpyxl
```

### Database support
```bash
pip install sqlalchemy
```

### All dependencies
```bash
pip install openpyxl sqlalchemy
```

## File Structure

```
tests/data/
├── __init__.py
├── test_data_provider.py      # Base class + implementations
├── test_data_factory.py       # Factory for creating providers
├── generate_test_data.py      # Generate test data
├── conftest.py                # pytest fixtures
├── README.md                  # This file
├── test_data.xlsx             # Excel test data (generated)
├── test_data.json             # JSON test data (generated)
└── test_data.db               # SQLite database (generated)
```

## Data Sheet Structure

### Members Sheet

| Column | Type | Example |
|--------|------|---------|
| id | Integer | 1 |
| first_name | String | John |
| last_name | String | Doe |
| designation | String | Senior Trainer |
| test_type | String | happy_path, update_first, delete_test |
| description | String | Test description |

### Courses Sheet

| Column | Type | Example |
|--------|------|---------|
| id | Integer | 1 |
| course_name | String | Python 101 |
| faculty_id | Integer | 1 |
| category | String | Programming |
| start_date | String | 2024-01-15 |
| end_date | String | 2024-03-15 |
| test_type | String | happy_path |
| description | String | Test description |

### Students Sheet

| Column | Type | Example |
|--------|------|---------|
| id | Integer | 1 |
| name | String | Mark Johnson |
| email | String | mark@test.com |
| course_id | Integer | 1 |
| skills | String | Python, Django |
| resume_url | String | https://example.com/resume.pdf |
| test_type | String | happy_path |
| description | String | Test description |

## Benefits

✅ **Pluggable**: Swap providers without changing test code
✅ **Flexible**: Support Excel, JSON, and Database sources
✅ **Extensible**: Easy to add new provider implementations
✅ **Non-technical**: Non-developers can manage Excel data
✅ **Centralized**: All test data in one place
✅ **Multiple Access Patterns**: Sequential, lookup, filter, random
✅ **Type-safe**: Consistent data structure across providers
✅ **Factory Pattern**: Auto-detection and creation of providers

## Troubleshooting

### FileNotFoundError for test data

```bash
# Generate test data first
cd tests/data
python generate_test_data.py
```

### ImportError for Excel support

```bash
pip install openpyxl
```

### ImportError for Database support

```bash
pip install sqlalchemy
```

### Provider not detected

```python
# Explicitly specify provider type
from test_data_provider import DataSourceType

provider = TestDataFactory.create_provider(
    "my_data.xlsx",
    provider_type=DataSourceType.EXCEL
)
```

## Contributing

To add a new provider:

1. Create new class inheriting from `TestDataProvider`
2. Implement abstract methods: `load()`, `get_all_data()`, `get_next_data()`
3. Register in `TestDataFactory._detect_provider_type()`
4. Update factory `create_provider()` method
5. Add tests and documentation

Example:

```python
class CSVTestDataProvider(TestDataProvider):
    def __init__(self, csv_path: str):
        super().__init__(csv_path)
        self.load()
    
    def load(self):
        # Implementation
        pass
    
    def get_all_data(self, sheet_name: str) -> List[Dict]:
        # Implementation
        pass
    
    def get_next_data(self, sheet_name: str) -> Dict:
        # Implementation
        pass
```
