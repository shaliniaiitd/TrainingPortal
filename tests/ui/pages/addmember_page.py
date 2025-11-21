"""
Add Member Page Object - represents the form for adding new members.
"""

from .base_page import BasePage


class AddMemberPage(BasePage):
    """Page object for add member form page."""

    # Locators - handling multiple possible selectors
    FIRST_NAME_INPUT = "[name='firstname']"
    LAST_NAME_INPUT = "[name='lastname'], #id_lastname"
    DESIGNATION_INPUT = "[name='designation'], #id_designation"
    DESIGNATION_SELECT = "select[name='designation']"
    EMAIL_INPUT = "[name='email'], #id_email"
    PHONE_INPUT = "[name='phone'], #id_phone"
    IMAGE_INPUT = "input[type='file']"
    SAVE_BTN = "input[type='submit']"
    CANCEL_BTN = "a:has-text('Cancel'), button:has-text('Cancel')"
    FORM_ELEMENT = "form"
    TITLE = "ADD MEMBER"

    def goto_page(self) -> "AddMemberPage":
        """Navigate to add member page."""
        self.goto("/myapp/members/addmember/")
        return self

    def is_form_loaded(self) -> bool:
        """Check if add member form is loaded."""
        return self.is_element_visible(self.FORM_ELEMENT)

    def fill_first_name(self, first_name: str) -> "AddMemberPage":
        """Fill first name field."""
        self.fill_input(self.FIRST_NAME_INPUT, first_name)
        return self

    def fill_last_name(self, last_name: str) -> "AddMemberPage":
        """Fill last name field."""
        self.fill_input(self.LAST_NAME_INPUT, last_name)
        return self

    def fill_designation(self, designation: str) -> "AddMemberPage":
        """Fill designation field."""
        # Try dropdown first, then text input
        if self.element_count(self.DESIGNATION_SELECT) > 0:
            self.select_option_by_text(self.DESIGNATION_SELECT, designation)
        else:
            self.fill_input(self.DESIGNATION_INPUT, designation)
        return self

    def fill_email(self, email: str) -> "AddMemberPage":
        """Fill email field."""
        self.fill_input(self.EMAIL_INPUT, email)
        return self

    def fill_phone(self, phone: str) -> "AddMemberPage":
        """Fill phone field."""
        self.fill_input(self.PHONE_INPUT, phone)
        return self

    def upload_image(self, file_path: str) -> "AddMemberPage":
        """Upload member image."""
        self.upload_file(self.IMAGE_INPUT, file_path)
        return self

    def fill_form(self, member_data: dict) -> "AddMemberPage":
        """
        Fill entire member form with data dict.
        
        Args:
            member_data: Dict with keys: first_name, last_name, designation, email, phone, image
        """
        if "first_name" in member_data:
            self.fill_first_name(member_data["first_name"])
        if "last_name" in member_data:
            self.fill_last_name(member_data["last_name"])
        if "designation" in member_data:
            self.fill_designation(member_data["designation"])
        if "email" in member_data:
            self.fill_email(member_data["email"])
        if "phone" in member_data:
            self.fill_phone(member_data["phone"])
        if "image" in member_data and member_data["image"]:
            self.upload_image(member_data["image"])
        return self

    def submit_form(self) -> None:
        """Submit the form."""
        self.click_element(self.SAVE_BTN)
        self.wait_for_load_state("networkidle")

    def cancel_form(self) -> None:
        """Cancel form and go back."""
        self.click_element(self.CANCEL_BTN)
        self.wait_for_load_state("networkidle")

    def get_first_name_value(self) -> str:
        """Get current first name value."""
        return self.get_input_value(self.FIRST_NAME_INPUT)

    def get_last_name_value(self) -> str:
        """Get current last name value."""
        return self.get_input_value(self.LAST_NAME_INPUT)

    def get_designation_value(self) -> str:
        """Get current designation value."""
        try:
            return self.get_input_value(self.DESIGNATION_SELECT)
        except:
            return self.get_input_value(self.DESIGNATION_INPUT)

    def get_email_value(self) -> str:
        """Get current email value."""
        return self.get_input_value(self.EMAIL_INPUT)

    def get_phone_value(self) -> str:
        """Get current phone value."""
        return self.get_input_value(self.PHONE_INPUT)

    def is_first_name_visible(self) -> bool:
        """Check if first name field is visible."""
        return self.is_element_visible(self.FIRST_NAME_INPUT)

    def is_last_name_visible(self) -> bool:
        """Check if last name field is visible."""
        return self.is_element_visible(self.LAST_NAME_INPUT)

    def is_designation_visible(self) -> bool:
        """Check if designation field is visible."""
        return self.is_element_visible(self.DESIGNATION_INPUT) or self.is_element_visible(self.DESIGNATION_SELECT)

    def is_submit_button_visible(self) -> bool:
        """Check if submit button is visible."""
        return self.is_element_visible(self.SUBMIT_BTN)

    def get_page_heading(self) -> str:
        """Get page heading."""
        return self.get_element_text(self.PAGE_HEADING)
