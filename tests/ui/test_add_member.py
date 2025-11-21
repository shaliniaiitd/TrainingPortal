import pytest
from TrainingPortal.tests.ui.base_test import BaseTestClass
@pytest.mark.page("addmember")
class TestMemberCreation(BaseTestClass):


    def test_add_member_page_loaded(self,page_obj):

        self.assert_page_loaded(page_obj, "is_form_loaded")

        # Build form using FormBuilder (fluent) — demonstrates Builder usage
        form = (
            self.build_form("member")
            .add_text("first_name", page_obj.FIRST_NAME_INPUT, "TestFirst")
            .add_text("last_name", page_obj.LAST_NAME_INPUT, "TestLast")
            .add_text("designation", page_obj.DESIGNATION_INPUT, "Automated Tester")
            .build()
        )

        # Fill via builder (delegates to page object's BasePage methods)
        form.fill(page_obj)
        page_obj.submit_form()

        members = self.get_page("members")

        # Start at members
        members.goto_page()
        assert "/members" in members.get_current_url()