"""
Update Member Page Object - represents the form for updating members.
Extends AddMemberPage since update form is similar to add form.
"""
import time

from .addmember_page import AddMemberPage


class UpdateMemberPage(AddMemberPage):
    """Page object for update member form page."""

    # Additional locators specific to update page
    CANCEL_BTN = "a:has-text('Cancel'), a:has-text('Back'), button:has-text('Cancel')"

    def goto_page(self, member_id: int) -> "UpdateMemberPage":
        """Navigate to update member page by member ID."""
        self.goto(f"/myapp/members/update/{member_id}"),
        time.sleep(2)
        return self

    def is_update_form_loaded(self) -> bool:
        """Check if update member form is loaded with prepopulated data."""
        # Form should be loaded and have values print(f"FIRST NAME VALUE = {self.get_first_name_value()}")
        print(f"FIRST NAME VALUE = {self.get_first_name_value()}")
        print(f"FORM LOADING = {self.is_form_loaded()}")

        return self.is_form_loaded() and self.get_first_name_value() != ""

    def verify_prepopulated_data(self, expected_data: dict) -> bool:
        """
        Verify that form is prepopulated with expected data.
        
        Args:
            expected_data: Dict with expected values
            
        Returns:
            True if all visible fields match expected data
        """
        if "first_name" in expected_data:
            if self.get_first_name_value() != expected_data["first_name"]:
                return False
        if "last_name" in expected_data:
            if self.get_last_name_value() != expected_data["last_name"]:
                return False
        if "email" in expected_data:
            if self.get_email_value() != expected_data["email"]:
                return False
        return True

    def update_first_name(self, first_name: str) -> "UpdateMemberPage":
        """Update first name field."""
        self.clear_input(self.FIRST_NAME_INPUT)
        self.fill_first_name(first_name)
        return self

    def update_last_name(self, last_name: str) -> "UpdateMemberPage":
        """Update last name field."""
        self.clear_input(self.LAST_NAME_INPUT)
        self.fill_last_name(last_name)
        return self

    def update_designation(self, designation: str) -> "UpdateMemberPage":
        """Update designation field."""
        self.clear_input(self.DESIGNATION_INPUT)
        self.fill_designation(designation)
        return self

    def update_email(self, email: str) -> "UpdateMemberPage":
        """Update email field."""
        self.clear_input(self.EMAIL_INPUT)
        self.fill_email(email)
        return self

    def update_phone(self, phone: str) -> "UpdateMemberPage":
        """Update phone field."""
        self.clear_input(self.PHONE_INPUT)
        self.fill_phone(phone)
        return self

    def update_form(self, member_data: dict) -> "UpdateMemberPage":
        """
        Update member form with new data.
        Only updates fields that are provided in member_data dict.
        
        Args:
            member_data: Dict with fields to update
        """
        if "first_name" in member_data:
            self.update_first_name(member_data["first_name"])
        if "last_name" in member_data:
            self.update_last_name(member_data["last_name"])
        if "designation" in member_data:
            self.update_designation(member_data["designation"])
        if "email" in member_data:
            self.update_email(member_data["email"])
        if "phone" in member_data:
            self.update_phone(member_data["phone"])
        return self

    def submit_update(self) -> None:
        """Submit the update form."""
        self.submit_form()
