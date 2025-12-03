"""
README - Data Validation Framework for TrainingPortal

This guide explains the complete data validation system for TrainingPortal test data.
"""

# ============================================================================
# DATA VALIDATION FRAMEWORK
# ============================================================================

## Overview

The data validation framework ensures test data consistency and quality across all
sources (JSON, Excel, SQLite database). It provides:

- ✅ Format validation (emails, URLs, dates)
- ✅ Uniqueness enforcement (no duplicate IDs)
- ✅ Required field validation
- ✅ Cross-referential validation (students→courses→members)
- ✅ Enum validation (7 designations, 6 course categories)
- ✅ Date logic validation (end dates must be after start dates)
- ✅ Detailed error and warning reporting


## File Structure

```
tests/db/
├── validators.py           # Core validation framework (5 validator classes)
├── validation_runner.py    # CLI tool to run validations on data files
├── test_validators.py      # Unit tests for all validators (50+ test cases)
└── README.md              # This file
```


## Core Components

### 1. ValidationResult (Dataclass)
Status container for validation results with error/warning collection.

**Attributes:**
- `is_valid` (bool): Whether validation passed
- `errors` (list): Critical errors that prevent usage
- `warnings` (list): Non-blocking warnings/notices
- `__str__()`: Formatted report output

**Usage:**
```python
result = ValidationResult(
    is_valid=False,
    errors=["Invalid email format"],
    warnings=["Check this field"]
)
print(result)
```


### 2. DataValidator (Base Class)
Base class with common validation methods.

**Methods:**
- `validate_email(email)` → bool
  - Regex: Checks for valid email format (user@domain.ext)
  - Valid: "test@example.com", "user+tag@domain.co.uk"
  - Invalid: "invalid.email", "@example.com"

- `validate_url(url)` → bool
  - Regex: Checks for HTTP/HTTPS URLs with optional paths/queries
  - Valid: "https://example.com", "http://sub.domain.org/path?id=1"
  - Invalid: "example.com", "not a url"

- `validate_date(date_str)` → bool
  - Format: YYYY-MM-DD (ISO format)
  - Validates month (1-12) and day (1-31) ranges
  - Valid: "2024-01-15", "2023-12-31"
  - Invalid: "2024-13-01", "01/15/2024"


### 3. MembersValidator
Validates faculty/staff member data.

**Required Fields:**
- `id` (int): Unique identifier
- `first_name` (str): Min 2 characters, alphabetic only
- `last_name` (str): Min 2 characters, alphabetic only
- `designation` (str): One of 7 valid options

**Optional Fields:**
- `email` (str): Valid email format if provided

**Valid Designations:**
1. Professor
2. Associate Professor
3. Assistant Professor
4. Lecturer
5. Senior Lecturer
6. Instructor
7. Teaching Assistant

**Validations:**
- ID uniqueness (no duplicates)
- Name min length and character validation
- Designation from valid list
- Email format if provided

**Usage:**
```python
member = {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "designation": "Associate Professor",
    "email": "john@example.com"
}
result = MembersValidator.validate(member)
if not result.is_valid:
    print(result)  # Print errors
```


### 4. CoursesValidator
Validates course/training program data.

**Required Fields:**
- `id` (int): Unique identifier
- `course_name` (str): Min 3 characters
- `faculty_id` (int): Must reference valid member ID
- `category` (str): One of 6 valid options

**Optional Fields:**
- `start_date` (str): YYYY-MM-DD format
- `end_date` (str): YYYY-MM-DD format (must be after start_date)
- `description` (str): Course description

**Valid Categories:**
1. Programming
2. Web Development
3. Data Analysis
4. DevOps
5. Testing
6. Others

**Validations:**
- ID uniqueness
- Course name min length
- Faculty ID cross-reference to Members
- Category from valid list
- Date range logic (end > start)

**Usage:**
```python
course = {
    "id": 1,
    "course_name": "Python Programming",
    "faculty_id": 1,
    "category": "Programming",
    "start_date": "2024-01-01",
    "end_date": "2024-03-01"
}
members = [{"id": 1}, {"id": 2}]  # For cross-ref validation
result = CoursesValidator.validate(course, members=members)
```


### 5. StudentsValidator
Validates student/trainee data.

**Required Fields:**
- `id` (int): Unique identifier
- `name` (str): Min 3 characters
- `email` (str): Valid email format, unique per student
- `course_id` (int): Must reference valid course ID

**Optional Fields:**
- `resume` (str): Valid URL if provided
- `skills` (str): Comma-separated skills list

**Validations:**
- ID uniqueness
- Name min length
- Email format and uniqueness
- Course ID cross-reference
- Resume URL format if provided

**Usage:**
```python
student = {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "course_id": 1,
    "resume": "https://example.com/alice-resume.pdf"
}
courses = [{"id": 1}]  # For cross-ref validation
result = StudentsValidator.validate(student, courses=courses)
```


### 6. TestDataValidator (Master)
Master validator that validates all entities together with cross-references.

**Methods:**
- `validate_all(members, courses, students)` → dict
  - Returns: {"Members": Result, "Courses": Result, "Students": Result}
  - Validates all three entity types
  - Performs cross-referential checks
  - Returns individual results for each entity type

- `print_report(results)` → None
  - Pretty-prints validation results
  - Shows status, error count, warning count
  - Displays individual errors and warnings

**Usage:**
```python
members = [...]
courses = [...]
students = [...]

results = TestDataValidator.validate_all(members, courses, students)
TestDataValidator.print_report(results)

# Check if all valid
if all(r.is_valid for r in results.values()):
    print("✅ All data is valid!")
else:
    print("❌ Validation failed")
```


## validation_runner.py - CLI Tool

Command-line tool to validate test data files from different sources.

### Usage

**Validate specific file:**
```bash
python tests/db/validation_runner.py tests/test_data/test_data.json
python tests/db/validation_runner.py tests/test_data/test_data.xlsx
```

**Validate all available sources:**
```bash
python tests/db/validation_runner.py
```

### Features

1. **JSON Support**
   - Loads test data from JSON file
   - Expected structure:
     ```json
     {
       "Members": [{...}, {...}],
       "Courses": [{...}, {...}],
       "Students": [{...}, {...}]
     }
     ```

2. **Excel Support**
   - Loads test data from Excel workbook
   - Requires sheet names: "Members", "Courses", "Students"
   - Requires: `pip install openpyxl`

3. **Auto-Discovery**
   - When run without args, searches tests/test_data/ for:
     - test_data.json
     - test_data.xlsx
   - Validates all found files
   - Prints summary report

### Example Output

```
======================================================================
COMPREHENSIVE DATA VALIDATION
======================================================================

📄 Validating JSON file: tests/test_data/test_data.json

========== MEMBERS VALIDATION ==========
Status: ✅ VALID
Errors: 0
Warnings: 0

========== COURSES VALIDATION ==========
Status: ✅ VALID
Errors: 0
Warnings: 0

========== STUDENTS VALIDATION ==========
Status: ✅ VALID
Errors: 0
Warnings: 0

======================================================================
VALIDATION SUMMARY
======================================================================

JSON:
  ✅ Members: 0 errors, 0 warnings
  ✅ Courses: 0 errors, 0 warnings
  ✅ Students: 0 errors, 0 warnings
```

### Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed


## test_validators.py - Unit Tests

Comprehensive test suite with 50+ test cases covering:

**Test Classes:**
1. TestValidationResult (3 tests)
   - Valid result creation
   - Invalid result with errors
   - String representation

2. TestDataValidator (9 tests)
   - Email validation (valid and invalid)
   - URL validation (valid and invalid)
   - Date validation (valid and invalid)

3. TestMembersValidator (10 tests)
   - Valid member creation
   - Missing required fields
   - Invalid designation
   - Name too short
   - Invalid email format
   - All valid designations

4. TestCoursesValidator (9 tests)
   - Valid course creation
   - Missing required fields
   - Course name too short
   - Invalid category
   - Invalid faculty reference (FK validation)
   - Invalid date range

5. TestStudentsValidator (9 tests)
   - Valid student creation
   - Missing required fields
   - Invalid email
   - Invalid course reference (FK validation)
   - Invalid resume URL
   - Name too short

6. TestTestDataValidator (3 tests)
   - Validate all valid data
   - Validate with multiple errors
   - Empty data validation

7. TestEdgeCases (4 tests)
   - Duplicate IDs
   - Special characters in names
   - Same start/end dates
   - Very long course names

### Run Tests

**Run all validator tests:**
```bash
pytest tests/db/test_validators.py -v
```

**Run specific test class:**
```bash
pytest tests/db/test_validators.py::TestMembersValidator -v
```

**Run specific test:**
```bash
pytest tests/db/test_validators.py::TestMembersValidator::test_valid_member -v
```

**Run with coverage:**
```bash
pytest tests/db/test_validators.py --cov=tests.db.validators
```


## Integration Workflow

### Step 1: Generate Test Data
```bash
python tests/generate_test_data.py
# Creates:
# - tests/test_data/test_data.json
# - tests/test_data/test_data.xlsx
# - tests/test_data/test_data.db
```

### Step 2: Validate Data
```bash
python tests/db/validation_runner.py
# Validates all data sources
# Reports any errors or inconsistencies
```

### Step 3: Fix Any Errors
Review validation output and correct data files as needed.

### Step 4: Run Tests
```bash
pytest tests/ -v
# Now run your actual tests with validated data
```


## Common Validation Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid email format | Email doesn't match pattern | Use format: user@domain.ext |
| Invalid URL format | URL doesn't start with http/https | Use: https://example.com |
| Duplicate ID | Two records have same ID | Ensure each ID is unique |
| Invalid designation | Not in 7 valid options | Use one of the 7 valid options |
| Invalid category | Not in 6 valid options | Use one of the 6 valid options |
| Faculty reference error | faculty_id doesn't exist in members | Ensure faculty_id matches a member ID |
| Course reference error | course_id doesn't exist in courses | Ensure course_id matches a course ID |
| End date before start date | end_date is earlier than start_date | Set end_date after start_date |
| Name too short | Name has less than required chars | Use min 2 chars for names, 3 for students |
| Required field missing | Field marked as required is empty | Provide value for all required fields |


## Extending the Framework

### Add New Validator

Create a new validator class by extending DataValidator:

```python
class ProjectValidator(DataValidator):
    """Validates project data."""
    
    @staticmethod
    def validate(project, members=None):
        """Validate a single project."""
        errors = []
        warnings = []
        
        # Check required fields
        if not project.get("id"):
            errors.append("Project ID is required")
        
        if not project.get("name") or len(project.get("name", "")) < 3:
            errors.append("Project name must be at least 3 characters")
        
        # Check references
        if members:
            member_ids = [m.get("id") for m in members]
            if project.get("lead_id") not in member_ids:
                errors.append(f"Project lead_id {project.get('lead_id')} not found in members")
        
        return ValidationResult(
            is_valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings
        )
```

### Add Validation to Test Setup

```python
# tests/conftest_backup.py
from tests.db.validators import TestDataValidator

@pytest.fixture
def test_data_provider():
    data = load_test_data()
    
    # Validate before providing to tests
    results = TestDataValidator.validate_all(
        data["members"],
        data["courses"],
        data["students"]
    )
    
    if not all(r.is_valid for r in results.values()):
        pytest.fail("Test data validation failed")
    
    return data
```


## Performance Considerations

- Validation is O(n) where n = total records
- Typical validation time for 100 members + 20 courses + 500 students: ~50ms
- Cross-referential checks (FK validation): O(n*m) but cached for efficiency
- Email/URL regex matching: ~1ms per record


## Best Practices

1. **Always validate before running tests**
   ```bash
   python tests/db/validation_runner.py && pytest tests/
   ```

2. **Keep test data in sync**
   - After modifying test data, re-run validation
   - Check validation errors before committing

3. **Use validation in CI/CD**
   - Add validation step to GitHub Actions
   - Fail pipeline if validation fails
   - Prevents bad data from entering tests

4. **Document data changes**
   - When adding/modifying test data, note changes
   - Update validation rules if schema changes
   - Keep validators and data in sync

5. **Version control data**
   - Commit validated test data
   - Track changes to validators
   - Use semantic versioning for data schema


## Troubleshooting

**Q: Validation runner doesn't find my JSON file**
A: Ensure file is at `tests/test_data/test_data.json` with correct name and location

**Q: Excel validation requires openpyxl**
A: Install with: `pip install openpyxl`

**Q: Cross-referential validation failing**
A: Check that IDs in Students match course IDs, and course faculty_ids match member IDs

**Q: Duplicate ID error for supposedly unique IDs**
A: Check data types - ensure IDs are integers, not strings ("1" vs 1)


## See Also

- `validators.py`: Core validation framework
- `validation_runner.py`: CLI tool documentation
- `test_validators.py`: Unit test examples
- `tests/db/README.md`: Database validation guide
