Playwright Automation Framework (Python)

This folder contains a UI + API automation framework for the TrainingPortal LMS, implemented using Playwright (Python).

Supports:

UI testing

API testing via Playwright request context

ORM-based database validation

Page Object Model

PageFactory

BaseTestClass

CI/CD workflows

📁 Folder Structure
tests/
├── ui/
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── page_factory.py
│   │   ├── home_page.py
│   │   ├── members_page.py
│   │   ├── add_member_page.py
│   │   ├── courses_page.py
│   │   └── ...
│   ├── base_test.py
│   ├── test_homepage.py
│   ├── test_members_crud.py
│   └── test_courses_crud.py
├── api/
│   └── test_members_api.py
├── db/
│   └── test_members_db.py

🧱 Framework Components
✔ BasePage

Element find/wait helpers

Text and visibility assertions

Navigation helpers

Dynamic selector utilities

✔ PageFactory

Dynamic loader:

page = PageFactory.get_page("MembersPage", page)

✔ BaseTestClass

Browser/page setup

Navigation helpers

Custom assertions:

assert_page_loaded()

assert_element_visible()

🤖 API Testing (Playwright Request Context)
resp = request_context.post(
    "/myapp/api/members/",
    data={"firstname": "John", "lastname": "Doe"}
)
assert resp.ok

🗄️ DB Validation (ORM)
from myapp.models import Members

assert Members.objects.filter(firstname="John").exists()

🧪 Example UI Test
def test_add_member(self, page):
    members = PageFactory.get_page("MembersPage", page)

    members.goto()
    members.click_add_member()
    members.fill_member_form("John", "Doe", "Trainer")
    members.submit()

    assert members.is_member_present("John")

🚦 CI/CD (GitHub Actions)

Workflows included:

python-tests.yml

playwright-install.yml

lint.yml



