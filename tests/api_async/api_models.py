"""API Test Data Models and Validators.

Defines data classes for API request/response payloads and entity-specific
validators. Demonstrates encapsulation and composition patterns.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from enum import Enum


class CourseCategory(Enum):
    """Course category enum (matches Django choices)."""
    PROGRAMMING = "Programming"
    WEB_DEV = "Web Dev"
    DATA_ANALYSIS = "Data Analysis"
    DEVOPS = "DevOps"
    TESTING = "Testing"
    OTHERS = "Others"


@dataclass
class MemberRequest:
    """Request payload for creating/updating a member."""
    first_name: str
    last_name: str
    designation: str
    email: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dict."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MemberResponse:
    """Response payload from member API."""
    id: int
    first_name: str
    last_name: str
    designation: str
    email: Optional[str] = None
    phone: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemberResponse":
        """Create from API response dict."""
        return cls(
            id=data.get("id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            designation=data.get("designation"),
            email=data.get("email"),
            phone=data.get("phone")
        )


@dataclass
class CourseRequest:
    """Request payload for creating/updating a course."""
    course_name: str
    facultyname_id: int
    category: str  # Use CourseCategory value
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dict."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CourseResponse:
    """Response payload from course API."""
    id: int
    course_name: str
    facultyname_id: int
    facultyname: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CourseResponse":
        """Create from API response dict."""
        return cls(
            id=data.get("id"),
            course_name=data.get("course_name"),
            facultyname_id=data.get("facultyname_id"),
            facultyname=data.get("facultyname"),
            category=data.get("category"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            description=data.get("description")
        )


@dataclass
class StudentRequest:
    """Request payload for creating/updating a student."""
    name: str
    course_id: int
    email: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dict."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class StudentResponse:
    """Response payload from student API."""
    id: int
    name: str
    course_id: int
    email: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentResponse":
        """Create from API response dict."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            course_id=data.get("course_id"),
            email=data.get("email"),
            resume_url=data.get("resume_url"),
            skills=data.get("skills")
        )


class ApiValidator:
    """Generic API validator with common validation rules."""

    @staticmethod
    def validate_member_response(data: Dict[str, Any]) -> MemberResponse:
        """Validate and parse member response."""
        required_fields = ["id", "first_name", "last_name", "designation"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        return MemberResponse.from_dict(data)

    @staticmethod
    def validate_course_response(data: Dict[str, Any]) -> CourseResponse:
        """Validate and parse course response."""
        required_fields = ["id", "course_name", "facultyname_id"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        return CourseResponse.from_dict(data)

    @staticmethod
    def validate_student_response(data: Dict[str, Any]) -> StudentResponse:
        """Validate and parse student response."""
        required_fields = ["id", "name", "course_id"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        return StudentResponse.from_dict(data)

    @staticmethod
    def validate_pagination_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate paginated list response (DRF format)."""
        required_fields = ["count", "results"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        return data

    @staticmethod
    def assert_field_not_empty(obj: Any, field: str):
        """Assert object field is not empty."""
        val = getattr(obj, field, None)
        assert val is not None and str(val).strip(), \
            f"Expected {field} to be non-empty, got: {val}"

    @staticmethod
    def assert_fields_match(obj1: Any, obj2: Any, fields: List[str]):
        """Assert fields match between two objects."""
        for field in fields:
            val1 = getattr(obj1, field, None)
            val2 = getattr(obj2, field, None)
            assert val1 == val2, \
                f"Field mismatch {field}: {val1} != {val2}"
