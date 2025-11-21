"""
Data Validation Module - validators.py

Validates TrainingPortal test data for correctness and consistency.
Ensures all test data meets business requirements and constraints.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __str__(self):
        status = "✅ PASS" if self.is_valid else "❌ FAIL"
        msg = f"{status}\n"
        if self.errors:
            msg += f"Errors ({len(self.errors)}):\n"
            for err in self.errors:
                msg += f"  ❌ {err}\n"
        if self.warnings:
            msg += f"Warnings ({len(self.warnings)}):\n"
            for warn in self.warnings:
                msg += f"  ⚠️  {warn}\n"
        return msg


class DataValidator:
    """Base validator for TrainingPortal data."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
        """Validate date format."""
        try:
            datetime.strptime(str(date_str), fmt)
            return True
        except (ValueError, TypeError):
            return False


class MembersValidator(DataValidator):
    """Validates Members test data."""
    
    REQUIRED_FIELDS = ["id", "first_name", "last_name", "designation"]
    VALID_DESIGNATIONS = [
        "Trainer", "Senior Trainer", "Junior Trainer", 
        "Lead Trainer", "Coordinator", "Manager", "Assistant"
    ]
    
    @classmethod
    def validate(cls, members: List[Dict[str, Any]]) -> ValidationResult:
        """Validate members data."""
        errors = []
        warnings = []
        
        if not members:
            errors.append("Members list is empty")
            return ValidationResult(False, errors, warnings)
        
        ids_seen = set()
        
        for idx, member in enumerate(members):
            member_errors = cls._validate_member(member, idx, ids_seen)
            errors.extend(member_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def _validate_member(cls, member: Dict[str, Any], idx: int, ids_seen: set) -> List[str]:
        """Validate single member."""
        errors = []
        prefix = f"Member[{idx}]"
        
        for field in cls.REQUIRED_FIELDS:
            if field not in member:
                errors.append(f"{prefix}: Missing required field '{field}'")
            elif not member[field]:
                errors.append(f"{prefix}: Field '{field}' is empty")
        
        if "id" in member:
            member_id = member["id"]
            if member_id in ids_seen:
                errors.append(f"{prefix}: Duplicate ID {member_id}")
            ids_seen.add(member_id)
        
        if "first_name" in member:
            first_name = str(member["first_name"])
            if len(first_name) < 2:
                errors.append(f"{prefix}: first_name too short (min 2 chars)")
            if not first_name.replace(" ", "").replace("-", "").isalpha():
                errors.append(f"{prefix}: first_name contains invalid characters")
        
        if "last_name" in member:
            last_name = str(member["last_name"])
            if len(last_name) < 2:
                errors.append(f"{prefix}: last_name too short (min 2 chars)")
            if not last_name.replace(" ", "").replace("-", "").isalpha():
                errors.append(f"{prefix}: last_name contains invalid characters")
        
        if "designation" in member:
            designation = member["designation"]
            if designation not in cls.VALID_DESIGNATIONS:
                errors.append(
                    f"{prefix}: Invalid designation '{designation}'. "
                    f"Valid: {', '.join(cls.VALID_DESIGNATIONS)}"
                )
        
        if "email" in member and member["email"]:
            if not cls.validate_email(str(member["email"])):
                errors.append(f"{prefix}: Invalid email format: {member['email']}")
        
        return errors


class CoursesValidator(DataValidator):
    """Validates Courses test data."""
    
    REQUIRED_FIELDS = ["id", "course_name", "faculty_id", "category"]
    VALID_CATEGORIES = [
        "Programming", "Web Dev", "Data Analysis", 
        "DevOps", "Testing", "Others"
    ]
    
    @classmethod
    def validate(cls, courses: List[Dict[str, Any]], member_ids: Optional[set] = None) -> ValidationResult:
        """Validate courses data."""
        errors = []
        warnings = []
        
        if not courses:
            errors.append("Courses list is empty")
            return ValidationResult(False, errors, warnings)
        
        ids_seen = set()
        
        for idx, course in enumerate(courses):
            course_errors = cls._validate_course(course, idx, ids_seen, member_ids)
            errors.extend(course_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def _validate_course(cls, course: Dict[str, Any], idx: int, ids_seen: set, 
                        member_ids: Optional[set] = None) -> List[str]:
        """Validate single course."""
        errors = []
        prefix = f"Course[{idx}]"
        
        for field in cls.REQUIRED_FIELDS:
            if field not in course:
                errors.append(f"{prefix}: Missing required field '{field}'")
            elif course[field] is None or str(course[field]).strip() == "":
                errors.append(f"{prefix}: Field '{field}' is empty")
        
        if "id" in course:
            course_id = course["id"]
            if course_id in ids_seen:
                errors.append(f"{prefix}: Duplicate ID {course_id}")
            ids_seen.add(course_id)
        
        if "course_name" in course:
            name = str(course["course_name"])
            if len(name) < 3:
                errors.append(f"{prefix}: course_name too short (min 3 chars)")
        
        if "faculty_id" in course and member_ids:
            faculty_id = course["faculty_id"]
            if faculty_id not in member_ids:
                errors.append(f"{prefix}: faculty_id {faculty_id} not found in members")
        
        if "category" in course:
            category = course["category"]
            if category not in cls.VALID_CATEGORIES:
                errors.append(
                    f"{prefix}: Invalid category '{category}'. "
                    f"Valid: {', '.join(cls.VALID_CATEGORIES)}"
                )
        
        if "start_date" in course and course["start_date"]:
            if not cls.validate_date(course["start_date"]):
                errors.append(f"{prefix}: Invalid start_date format: {course['start_date']}")
        
        if "end_date" in course and course["end_date"]:
            if not cls.validate_date(course["end_date"]):
                errors.append(f"{prefix}: Invalid end_date format: {course['end_date']}")
        
        if ("start_date" in course and "end_date" in course and 
            course["start_date"] and course["end_date"]):
            try:
                start = datetime.strptime(str(course["start_date"]), "%Y-%m-%d")
                end = datetime.strptime(str(course["end_date"]), "%Y-%m-%d")
                if end <= start:
                    errors.append(f"{prefix}: end_date must be after start_date")
            except ValueError:
                pass
        
        return errors


class StudentsValidator(DataValidator):
    """Validates Students test data."""
    
    REQUIRED_FIELDS = ["id", "name", "email", "course_id"]
    
    @classmethod
    def validate(cls, students: List[Dict[str, Any]], course_ids: Optional[set] = None) -> ValidationResult:
        """Validate students data."""
        errors = []
        warnings = []
        
        if not students:
            errors.append("Students list is empty")
            return ValidationResult(False, errors, warnings)
        
        ids_seen = set()
        emails_seen = set()
        
        for idx, student in enumerate(students):
            student_errors = cls._validate_student(student, idx, ids_seen, emails_seen, course_ids)
            errors.extend(student_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def _validate_student(cls, student: Dict[str, Any], idx: int, 
                         ids_seen: set, emails_seen: set,
                         course_ids: Optional[set] = None) -> List[str]:
        """Validate single student."""
        errors = []
        prefix = f"Student[{idx}]"
        
        for field in cls.REQUIRED_FIELDS:
            if field not in student:
                errors.append(f"{prefix}: Missing required field '{field}'")
            elif student[field] is None or str(student[field]).strip() == "":
                errors.append(f"{prefix}: Field '{field}' is empty")
        
        if "id" in student:
            student_id = student["id"]
            if student_id in ids_seen:
                errors.append(f"{prefix}: Duplicate ID {student_id}")
            ids_seen.add(student_id)
        
        if "name" in student:
            name = str(student["name"])
            if len(name) < 3:
                errors.append(f"{prefix}: name too short (min 3 chars)")
        
        if "email" in student:
            email = str(student["email"])
            if not cls.validate_email(email):
                errors.append(f"{prefix}: Invalid email format: {email}")
            if email in emails_seen:
                errors.append(f"{prefix}: Duplicate email: {email}")
            emails_seen.add(email)
        
        if "course_id" in student and course_ids:
            course_id = student["course_id"]
            if course_id not in course_ids:
                errors.append(f"{prefix}: course_id {course_id} not found in courses")
        
        if "resume_url" in student and student["resume_url"]:
            url = str(student["resume_url"])
            if not cls.validate_url(url):
                errors.append(f"{prefix}: Invalid resume_url format: {url}")
        
        if "skills" in student and student["skills"]:
            skills = str(student["skills"])
            if len(skills.strip()) == 0:
                errors.append(f"{prefix}: Invalid skills format")
        
        return errors


class TestDataValidator:
    """Main validator for complete test dataset."""
    
    @classmethod
    def validate_all(cls, members: List[Dict], courses: List[Dict], 
                    students: List[Dict]) -> Dict[str, ValidationResult]:
        """Validate all test data with cross-referential checks."""
        results = {}
        
        members_result = MembersValidator.validate(members)
        results["members"] = members_result
        
        member_ids = {m["id"] for m in members if "id" in m} if members else set()
        
        courses_result = CoursesValidator.validate(courses, member_ids)
        results["courses"] = courses_result
        
        course_ids = {c["id"] for c in courses if "id" in c} if courses else set()
        
        students_result = StudentsValidator.validate(students, course_ids)
        results["students"] = students_result
        
        return results
    
    @classmethod
    def print_report(cls, results: Dict[str, ValidationResult]) -> None:
        """Print validation report."""
        print("\n" + "=" * 70)
        print("DATA VALIDATION REPORT")
        print("=" * 70)
        
        all_valid = True
        for entity_name, result in results.items():
            print(f"\n{entity_name.upper()}:")
            print("-" * 70)
            print(result)
            if not result.is_valid:
                all_valid = False
        
        print("=" * 70)
        if all_valid:
            print("✅ ALL VALIDATIONS PASSED")
        else:
            print("❌ SOME VALIDATIONS FAILED")
        print("=" * 70 + "\n")
