"""Member CRUD tests using PageFactory and Page Objects.

These tests use PageFactory to load page objects and exercise CRUD flows
for the Members entity. Tests demonstrate OOP usage (page objects, inheritance)
and use the Builder (FormBuilder) where helpful.
"""

import pytest
from TrainingPortal.tests.ui.base_test import BaseTestClass

@pytest.mark.page("members")
class TestMemberCreation(BaseTestClass):
    """CRUD tests for Members — inherits from BaseTestClass."""

    def test_member_page_loaded(self,page_obj):
        """Test: Create a new member."""

        count_before = page_obj.get_members_count()

        add_page = self.get_page("addmember")
        add_page.goto_page()
        assert "addmember" in add_page.get_current_url()
        self.assert_page_loaded(add_page, "is_form_loaded")

        # Build form using FormBuilder (fluent) — demonstrates Builder usage
        form = (
            self.build_form("member")
            .add_text("first_name", add_page.FIRST_NAME_INPUT, "TestFirst2")
            .add_text("last_name", add_page.LAST_NAME_INPUT, "TestLast2")
            .add_text("designation", add_page.DESIGNATION_INPUT, "Automated Tester")
            .build()
        )

        # Fill via builder (delegates to page object's BasePage methods)
        form.fill(add_page)
        add_page.submit_form()

        members = self.get_page("members")

        # Start at members
        members.goto_page()

        assert "/members" in members.get_current_url()

        count_after = page_obj.get_members_count()
        self.assert_count_increased(count_before, count_after, delta=1)
        assert members.member_exists("TestFirst2","TestLast2"), "Created member not found in list"
    @pytest.mark.page("member_detail", id = 1)
    def test_read_member_detail(self,page_obj):
        """Test: Read member details from detail page."""
        # detail = self.get_page("member_detail")
        # detail.goto_page(1)
        self.assert_page_loaded(page_obj, "is_detail_page_loaded")

        # Verify that a page heading is present (indicates page loaded with data)
        heading = page_obj.get_page_heading()
        assert "/detail" in page_obj.get_current_url()
        assert heading, "Member detail page has no heading"

    @pytest.mark.page("update_member", id = 10)
    def test_update_member(self,page_obj):
        """Test: Update member details."""
        # NOTE: This test assumes a member with id=10 exists

        assert "update" in page_obj.get_current_url()
        print( f"TITLE = {page_obj.page.title()}")
        self.assert_page_loaded(page_obj, "is_update_form_loaded")

        new_first = "Shalini"
        page_obj.update_first_name(new_first)
        page_obj.submit_update()

        # Verify update by checking detail page
        detail = self.get_page("member_detail")
        detail.goto_page(1)

        heading = detail.get_page_heading()
        assert new_first.lower() in str(heading).lower(), f"Updated name not found in heading: {heading}"

    @pytest.mark.page("member_list", id=10)
    def test_delete_member(self):
        """Test: Delete a member."""
        members = self.get_page("members")
        members.goto_members_list()
        initial = members.get_members_count()

        # Attempt delete first member if exists
        if initial == 0:
            pytest.skip("No members available to delete")

        members.click_delete_member(0)
        # Some apps show confirmation; try clicking first confirm button if present
        try:
            self.page.click("button:has-text('Confirm'), button:has-text('Yes')")
        except Exception:
            pass# def test_delete_member(self):
        """Test: Delete a member."""
        members = self.get_page("members")
        members.goto_members_list()  #     """Test: Delete a member."""

        initial = members.get_members_count()

        # Attempt delete first member if exists
        if initial == 0:
            pytest.skip("No members available to delete")

        members.click_delete_member(0)
        # Some apps show confirmation; try clicking first confirm b
        try:
            self.page.click("button:has-text('Confirm'), button:has
        except Exception:
            pass

        # Reload list and verify count decreased
        members.goto_members_list()
        after = members.get_members_count()
        self.assert_count_decreased(initial, after, delta=1)

        # Attempt delete first member if exists
        if initial == 0:
            pytest.skip("No members available to delete")

        members.click_delete_member(0)
        # Some apps show confirmation; try clicking first confirm button if present
        try:
            self.page.click("button:has-text('Confirm'), button:has-text('Yes')")
        except Exception:
            pass

        # Reload list and verify count decreased
        members.goto_members_list()
        after = members.get_members_count()
        self.assert_count_decreased(initial, after, delta=1)
        initial = members.get_members_count()

        # Attempt delete first member if exists
        if initial == 0:
            pytest.skip("No members available to delete")

        members.click_delete_member(0)
        # Some apps show confirmation; try clicking first confirm button if present
        try:
            self.page.click("button:has-text('Confirm'), button:has-text('Yes')")
        except Exception:
            pass

        # Reload list and verify count decreased
        members.goto_members_list()
        after = members.get_members_count()
        self.assert_count_decreased(initial, after, delta=1)


        # Reload list and verify count decreased
        members.goto_members_list()
        after = members.get_members_count()
        self.assert_count_decreased(initial, after, delta=1)
