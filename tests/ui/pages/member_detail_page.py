"""
Member Detail Page Object - represents the detail view of a single member.
"""

from .base_page import BasePage


class MemberDetailPage(BasePage):
    """Page object for member detail page."""

    # Locators
    PAGE_HEADING = "h1, h2"
    FIRST_NAME_TEXT = "text=First Name"
    LAST_NAME_TEXT = "text=Last Name"
    DESIGNATION_TEXT = "text=Designation"
    EMAIL_TEXT = "text=Email"
    PHONE_TEXT = "text=Phone"
    IMAGE_ELEMENT = "img"
    UPDATE_BTN = "a:has-text('Update'), button:has-text('Edit'), a:has-text('Edit')"
    DELETE_BTN = "a:has-text('Delete'), button:has-text('Delete')"
    BACK_BTN = "a:has-text('Back'), a:has-text('Back to Members')"
    MEMBER_INFO = ".member-info, .detail-view, [role='main']"

    def goto_page(self, member_id: int) -> "MemberDetailPage":
        """Navigate to member detail page by member ID."""
        self.goto(f"/myapp/members/detail/{member_id}")
        return self

    def is_detail_page_loaded(self) -> bool:
        """Check if detail page is loaded."""
        return self.is_element_visible(self.PAGE_HEADING)

    def get_first_name(self) -> str:
        """Get member's first name."""
        return self._get_field_value("First Name")

    def get_last_name(self) -> str:
        """Get member's last name."""
        return self._get_field_value("Last Name")

    def get_designation(self) -> str:
        """Get member's designation."""
        return self._get_field_value("Designation")

    def get_email(self) -> str:
        """Get member's email."""
        return self._get_field_value("Email")

    def get_phone(self) -> str:
        """Get member's phone."""
        return self._get_field_value("Phone")

    def _get_field_value(self, field_name: str) -> str:
        """Helper to extract field value from detail view."""
        try:
            # Try to find label followed by value
            locator = self.page.locator(f"text='{field_name}' >> following-sibling::*")
            if locator.count() > 0:
                return locator.text_content().strip()
            # Fallback: look for the field text and get next element
            return ""
        except:
            return ""

    def get_page_heading(self) -> str:
        """Get page heading."""
        return self.get_element_text(self.PAGE_HEADING)

    def click_update_button(self) -> None:
        """Click update button."""
        self.click_element(self.UPDATE_BTN)
        self.wait_for_load_state("networkidle")

    def click_delete_button(self) -> None:
        """Click delete button."""
        self.click_element(self.DELETE_BTN)
        self.wait_for_load_state("networkidle")

    def click_back_button(self) -> None:
        """Click back button."""
        self.click_element(self.BACK_BTN)
        self.wait_for_load_state("networkidle")

    def is_update_button_visible(self) -> bool:
        """Check if update button is visible."""
        return self.is_element_visible(self.UPDATE_BTN)

    def is_delete_button_visible(self) -> bool:
        """Check if delete button is visible."""
        return self.is_element_visible(self.DELETE_BTN)

    def has_member_image(self) -> bool:
        """Check if member has an image displayed."""
        return self.is_element_visible(self.IMAGE_ELEMENT)
