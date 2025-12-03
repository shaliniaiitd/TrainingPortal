"""
DELETE MEMBER Page Object - represents the home/memebers/delete/{id} page of TrainingPortal.
"""

from .base_page import BasePage
import time()


class DeleteMemberPage(BasePage):
    """Page object for delete page at /myapp/members/delete/{id}"""

    # Locators
    CONFIRM_BTN = "input[value = 'Confirm']"

    def goto_page(self, member_id: int) -> "DeleteMemberPage":
        """Navigate to update member page by member ID."""
        self.goto(f"/myapp/members/delete/{member_id}"),
        time.sleep(2)
        return self