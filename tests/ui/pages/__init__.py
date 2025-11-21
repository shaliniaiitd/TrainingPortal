"""
Page Objects Package

This package contains all Page Object classes for UI testing TrainingPortal.

Available pages:
- HomePage: Home page at /myapp/
- MembersPage: Members list page at /myapp/members/
- AddMemberPage: Add member form
- UpdateMemberPage: Update member form
- MemberDetailPage: Member detail view
- CoursesPage: Courses list page at /myapp/courses/
- AddCoursePage: Add course form
- UpdateCoursePage: Update course form
- CourseDetailPage: Course detail view

Usage with PageFactory:
    from page_factory import PageFactory
    home = PageFactory.get_page("home", page)
    members = PageFactory.get_page("members", page)

See page_factory.py for factory implementation.
"""

from .base_page import BasePage
from .page_factory import PageFactory
from .home_page import HomePage
from .members_page import MembersPage
from .addmember_page import AddMemberPage
from .update_member_page import UpdateMemberPage
from .member_detail_page import MemberDetailPage
from .courses_page import CoursesPage
from .add_course_page import AddCoursePage
from .update_course_page import UpdateCoursePage
from .course_detail_page import CourseDetailPage

__all__ = [
    "BasePage",
    "PageFactory",
    "HomePage",
    "MembersPage",
    "AddMemberPage",
    "UpdateMemberPage",
    "MemberDetailPage",
    "CoursesPage",
    "AddCoursePage",
    "UpdateCoursePage",
    "CourseDetailPage",
]
