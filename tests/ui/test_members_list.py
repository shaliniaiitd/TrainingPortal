import pytest
from TrainingPortal.tests.ui.base_test import BaseTestClass



class TestMemberCreation(BaseTestClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.members_page = self.get_page("members")
    """CRUD tests for Members — inherits from BaseTestClass."""


    def test_member_page_loaded(self):
        """Test: Create a new member."""
        self.members_page.goto_members_list()
        count_before = self.members_page.get_members_count()
        self.assert_page_loaded(self.members_page, "is_members_page_loaded")


    def  test_elements_visble(self):
