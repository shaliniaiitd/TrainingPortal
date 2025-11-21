"""
Members Page Object - represents the members list page.
"""

from .base_page import BasePage


class MembersPage(BasePage):
    """Page object for members list page at /myapp/members/"""

    EXPECTED_TITLE = 'Members'

    # Locators
    ADD_MEMBER_BTN = "a:has-text('Add Member'), button:has-text('Add Member')"
    MEMBERS_TABLE = "table"
    MEMBER_ROWS = "table tbody tr"
    MEMBER_NAME_CELLS = "table tbody tr td:first-child"
    DELETE_BTNS = "button:has-text('Delete'), a:has-text('Delete')"
    UPDATE_BTNS = "button:has-text('Update'), a:has-text('Update'), button:has-text('Edit')"
    MEMBERS_LINK = "a:has-text('Members')"
    HOME = "a:has-text('HOME')"

    def goto_page(self) -> "MembersPage":
        """Navigate to members list page."""
        self.goto("/myapp/members/")
        return self

    def is_members_page_loaded(self) -> bool:
        """Check if members page is loaded."""
        return self.page.title() == self.EXPECTED_TITLE

    def click_add_member(self) -> None:
        """Click Add Member button."""
        self.click_element(self.ADD_MEMBER_BTN)
        self.wait_for_load_state("networkidle")

    def get_members_count(self) -> int:
        """Get number of members in table."""
        return self.get_table_row_count(self.MEMBERS_TABLE)

    def get_members_names(self) -> list:
        """Get list of all member names."""
        return self.get_table_column_values(self.MEMBERS_TABLE, 0)

    def member_exists(self, first_name: str, last_name: str) -> bool:
        rows = self.page.locator("table tbody tr")
        row_texts = rows.all_text_contents()

        for row in row_texts:
            if first_name in row and last_name in row:
                return True
        return False

    def click_delete_member(self, member_index: int = 0) -> None:
        """Click delete button for a member."""
        delete_buttons = self.page.locator(self.DELETE_BTNS).all()
        if member_index < len(delete_buttons):
            delete_buttons[member_index].click()

    def click_update_member(self, member_index: int = 0) -> None:
        """Click update button for a member."""
        update_buttons = self.page.locator(self.UPDATE_BTNS).all()
        if member_index < len(update_buttons):
            update_buttons[member_index].click()
            self.wait_for_load_state("networkidle")

    def click_member_by_name(self, member_name: str) -> None:
        """Click on a member by name."""
        self.click_by_text(member_name)
        self.wait_for_load_state("networkidle")

    def get_page_heading(self) -> str:
        """Get page heading."""
        return self.get_element_text(self.EXPECTED_TITLE)

    def is_add_member_button_visible(self) -> bool:
        """Check if Add Member button is visible."""
        return self.is_element_visible(self.ADD_MEMBER_BTN)

    def has_table(self) -> bool:
        """Check if members table exists."""
        return self.element_count(self.MEMBERS_TABLE) > 0
