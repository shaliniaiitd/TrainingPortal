"""
Unit Tests for Data Validators - test_validators.py

Test suite for all validation classes with comprehensive coverage.
"""

import pytest
from datetime import date, timedelta
from validators import (
    ValidationResult,
    DataValidator,
    MembersValidator,
    CoursesValidator,
    StudentsValidator,
    TestDataValidator
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_valid_result_creation(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_invalid_result_with_errors(self):
        """Test creating an invalid result with errors."""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(is_valid=False, errors=errors, warnings=[])
        assert result.is_valid is False
        assert len(result.errors) == 2
    
    def test_result_str_representation(self):
        """Test string representation of result."""
        result = ValidationResult(
            is_valid=False,
            errors=["Invalid format"],
            warnings=["Check this"]
        )
        str_result = str(result)
        assert "Status: INVALID" in str_result
        assert "Errors:" in str_result
        assert "Warnings:" in str_result


class TestDataValidator:
    """Tests for DataValidator base class."""
    
    def test_valid_email(self):
        """Test email validation with valid emails."""
        validator = DataValidator()
        assert validator.validate_email("test@example.com") is True
        assert validator.validate_email("user.name+tag@domain.co.uk") is True
    
    def test_invalid_email(self):
        """Test email validation with invalid emails."""
        validator = DataValidator()
        assert validator.validate_email("invalid.email") is False
        assert validator.validate_email("@example.com") is False
        assert validator.validate_email("test@") is False
    
    def test_valid_url(self):
        """Test URL validation with valid URLs."""
        validator = DataValidator()
        assert validator.validate_url("https://example.com") is True
        assert validator.validate_url("http://sub.domain.co.uk/path") is True
        assert validator.validate_url("https://example.com/path?query=1") is True
    
    def test_invalid_url(self):
        """Test URL validation with invalid URLs."""
        validator = DataValidator()
        assert validator.validate_url("not a url") is False
        assert validator.validate_url("example.com") is False
        assert validator.validate_url("htp://broken.com") is False
    
    def test_valid_date(self):
        """Test date validation with valid dates."""
        validator = DataValidator()
        assert validator.validate_date("2024-01-15") is True
        assert validator.validate_date("2023-12-31") is True
    
    def test_invalid_date(self):
        """Test date validation with invalid dates."""
        validator = DataValidator()
        assert validator.validate_date("2024-13-01") is False
        assert validator.validate_date("2024-01-32") is False
        assert validator.validate_date("01-15-2024") is False
        assert validator.validate_date("not a date") is False


class TestMembersValidator:
    """Tests for MembersValidator."""
    
    def test_valid_member(self):
        """Test validation of a valid member."""
        member = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Assistant Professor"
        }
        result = MembersValidator.validate(member)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_valid_member_with_email(self):
        """Test validation of a valid member with email."""
        member = {
            "id": 1,
            "first_name": "Jane",
            "last_name": "Smith",
            "designation": "Professor",
            "email": "jane@example.com"
        }
        result = MembersValidator.validate(member)
        assert result.is_valid is True
    
    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        member = {
            "id": 1,
            "first_name": "John"
        }
        result = MembersValidator.validate(member)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_invalid_designation(self):
        """Test validation fails with invalid designation."""
        member = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Invalid Role"
        }
        result = MembersValidator.validate(member)
        assert result.is_valid is False
        assert any("designation" in str(e).lower() for e in result.errors)
    
    def test_invalid_name_too_short(self):
        """Test validation fails with name too short."""
        member = {
            "id": 1,
            "first_name": "J",
            "last_name": "Doe",
            "designation": "Professor"
        }
        result = MembersValidator.validate(member)
        assert result.is_valid is False
    
    def test_invalid_email_format(self):
        """Test validation fails with invalid email."""
        member = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Professor",
            "email": "invalid-email"
        }
        result = MembersValidator.validate(member)
        assert result.is_valid is False
    
    def test_all_valid_designations(self):
        """Test validation with all valid designations."""
        valid_designations = [
            "Professor", "Associate Professor", "Assistant Professor",
            "Lecturer", "Senior Lecturer", "Instructor", "Teaching Assistant"
        ]
        
        for designation in valid_designations:
            member = {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "designation": designation
            }
            result = MembersValidator.validate(member)
            assert result.is_valid is True, f"Failed for designation: {designation}"


class TestCoursesValidator:
    """Tests for CoursesValidator."""
    
    def test_valid_course(self):
        """Test validation of a valid course."""
        course = {
            "id": 1,
            "course_name": "Python Programming",
            "faculty_id": 1,
            "category": "Programming",
            "start_date": "2024-01-01",
            "end_date": "2024-03-01"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        assert result.is_valid is True
    
    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        course = {
            "id": 1,
            "course_name": "Python"
        }
        result = CoursesValidator.validate(course, members=[])
        assert result.is_valid is False
    
    def test_invalid_course_name_too_short(self):
        """Test validation fails with course name too short."""
        course = {
            "id": 1,
            "course_name": "AB",
            "faculty_id": 1,
            "category": "Programming"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        assert result.is_valid is False
    
    def test_invalid_category(self):
        """Test validation fails with invalid category."""
        course = {
            "id": 1,
            "course_name": "Python Course",
            "faculty_id": 1,
            "category": "Invalid Category"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        assert result.is_valid is False
    
    def test_invalid_faculty_reference(self):
        """Test validation fails with non-existent faculty."""
        course = {
            "id": 1,
            "course_name": "Python Course",
            "faculty_id": 999,
            "category": "Programming"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        assert result.is_valid is False
        assert any("faculty" in str(e).lower() for e in result.errors)
    
    def test_invalid_date_range(self):
        """Test validation fails with end_date before start_date."""
        course = {
            "id": 1,
            "course_name": "Python Course",
            "faculty_id": 1,
            "category": "Programming",
            "start_date": "2024-03-01",
            "end_date": "2024-01-01"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        assert result.is_valid is False
    
    def test_all_valid_categories(self):
        """Test validation with all valid categories."""
        valid_categories = [
            "Programming", "Web Development", "Data Analysis",
            "DevOps", "Testing", "Others"
        ]
        
        for category in valid_categories:
            course = {
                "id": 1,
                "course_name": "Test Course",
                "faculty_id": 1,
                "category": category
            }
            result = CoursesValidator.validate(course, members=[{"id": 1}])
            assert result.is_valid is True, f"Failed for category: {category}"


class TestStudentsValidator:
    """Tests for StudentsValidator."""
    
    def test_valid_student(self):
        """Test validation of a valid student."""
        student = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "course_id": 1
        }
        result = StudentsValidator.validate(student, courses=[{"id": 1}])
        assert result.is_valid is True
    
    def test_valid_student_with_resume(self):
        """Test validation of a valid student with resume."""
        student = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "course_id": 1,
            "resume": "https://example.com/resume.pdf"
        }
        result = StudentsValidator.validate(student, courses=[{"id": 1}])
        assert result.is_valid is True
    
    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        student = {
            "id": 1,
            "name": "Alice"
        }
        result = StudentsValidator.validate(student, courses=[])
        assert result.is_valid is False
    
    def test_invalid_email(self):
        """Test validation fails with invalid email."""
        student = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "invalid-email",
            "course_id": 1
        }
        result = StudentsValidator.validate(student, courses=[{"id": 1}])
        assert result.is_valid is False
    
    def test_invalid_course_reference(self):
        """Test validation fails with non-existent course."""
        student = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "course_id": 999
        }
        result = StudentsValidator.validate(student, courses=[{"id": 1}])
        assert result.is_valid is False
        assert any("course" in str(e).lower() for e in result.errors)
    
    def test_invalid_resume_url(self):
        """Test validation fails with invalid resume URL."""
        student = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "course_id": 1,
            "resume": "not-a-url"
        }
        result = StudentsValidator.validate(student, courses=[{"id": 1}])
        assert result.is_valid is False
    
    def test_name_too_short(self):
        """Test validation fails with name too short."""
        student = {
            "id": 1,
            "name": "AB",
            "email": "alice@example.com",
            "course_id": 1
        }
        result = StudentsValidator.validate(student, courses=[{"id": 1}])
        assert result.is_valid is False


class TestTestDataValidator:
    """Tests for TestDataValidator master validator."""
    
    def test_validate_all_valid_data(self):
        """Test validation of all valid data."""
        members = [
            {"id": 1, "first_name": "John", "last_name": "Doe", "designation": "Professor"}
        ]
        courses = [
            {"id": 1, "course_name": "Python 101", "faculty_id": 1, "category": "Programming"}
        ]
        students = [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "course_id": 1}
        ]
        
        results = TestDataValidator.validate_all(members, courses, students)
        
        assert results["Members"].is_valid is True
        assert results["Courses"].is_valid is True
        assert results["Students"].is_valid is True
    
    def test_validate_all_with_errors(self):
        """Test validation with multiple errors."""
        members = [
            {"id": 1, "first_name": "J", "last_name": "Doe", "designation": "Invalid"}
        ]
        courses = [
            {"id": 1, "course_name": "AB", "faculty_id": 999, "category": "Invalid"}
        ]
        students = [
            {"id": 1, "name": "A", "email": "invalid", "course_id": 999}
        ]
        
        results = TestDataValidator.validate_all(members, courses, students)
        
        assert results["Members"].is_valid is False
        assert results["Courses"].is_valid is False
        assert results["Students"].is_valid is False
    
    def test_empty_data_validation(self):
        """Test validation of empty data."""
        results = TestDataValidator.validate_all([], [], [])
        
        assert results["Members"].is_valid is True
        assert results["Courses"].is_valid is True
        assert results["Students"].is_valid is True


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_duplicate_member_ids(self):
        """Test detection of duplicate member IDs."""
        members = [
            {"id": 1, "first_name": "John", "last_name": "Doe", "designation": "Professor"},
            {"id": 1, "first_name": "Jane", "last_name": "Smith", "designation": "Associate Professor"}
        ]
        
        result = MembersValidator.validate_members_batch(members)
        assert result.is_valid is False
        assert any("duplicate" in str(e).lower() for e in result.errors)
    
    def test_member_name_with_special_characters(self):
        """Test member name validation with special characters."""
        member = {
            "id": 1,
            "first_name": "Jean-Pierre",
            "last_name": "O'Brien",
            "designation": "Professor"
        }
        result = MembersValidator.validate(member)
        # Should allow hyphens and apostrophes in names
        assert result.is_valid is True or len(result.warnings) > 0
    
    def test_course_with_same_start_end_date(self):
        """Test course validation with same start and end date."""
        course = {
            "id": 1,
            "course_name": "One Day Course",
            "faculty_id": 1,
            "category": "Programming",
            "start_date": "2024-01-01",
            "end_date": "2024-01-01"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        # Should be valid or have warning
        assert result.is_valid or len(result.warnings) > 0
    
    def test_very_long_course_name(self):
        """Test course validation with very long name."""
        course = {
            "id": 1,
            "course_name": "A" * 500,
            "faculty_id": 1,
            "category": "Programming"
        }
        result = CoursesValidator.validate(course, members=[{"id": 1}])
        # Should still be valid (no max length specified)
        assert result.is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
