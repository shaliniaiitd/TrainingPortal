"""
Base Page class providing common page functionality and utilities.
All page objects should inherit from this class.
"""

from playwright.sync_api import Page, Locator
from typing import Optional, List, Dict, Any
import time


class BasePage:
    """
    Base class for all page objects. Provides common methods for:
    - Navigation
    - Element location and interaction
    - Waiting and assertions
    - Form operations
    - File uploads
    """

    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8000"):
        self.page = page
        self.base_url = base_url
        self.page.set_default_timeout(5000)  # 5 seconds

    # ============================================================================
    # Navigation Methods
    # ============================================================================

    def goto(self, path: str) -> None:
        """Navigate to a specific path on the application."""
        url = f"{self.base_url}{path}"
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")


    # ============================================================================
    # Locator Methods
    # ============================================================================

    def get_locator_by_selector(self, selector: str) -> Locator:
        """Get locator using CSS selector."""
        return self.page.locator(selector)

    # def get_locator_by_text(self, text: str) -> Locator:
    #     """Get locator by text content."""
    #     return self.page.locator(f"text={text}")
    #
    # def get_locator_by_placeholder(self, placeholder: str) -> Locator:
    #     """Get locator by input placeholder."""
    #     return self.page.locator(f"[placeholder='{placeholder}']")
    #
    # def get_locator_by_name(self, name: str) -> Locator:
    #     """Get locator by element name attribute."""
    #     return self.page.locator(f"[name='{name}']")
    #
    # def get_locator_by_id(self, element_id: str) -> Locator:
    #     """Get locator by element ID."""
    #     return self.page.locator(f"#{element_id}")
    #
    # def get_locator_by_label(self, label_text: str) -> Locator:
    #     """Get locator for input by associated label text."""
    #     return self.page.locator(f"label:has-text('{label_text}') + input")
    #
    # # ============================================================================
    # # Element Interaction Methods
    # # ============================================================================

    def click_element(self, selector: str) -> None:
        """Click an element by selector."""
        self.page.locator(selector).click()

    def click_by_text(self, text: str) -> None:
        """Click element by text content."""
        self.page.locator(f"text={text}").click()

    def click_and_wait_for_load(self, selector: str, timeout: int = 5000) -> None:
        """Click an element and wait for page to load."""
        self.page.locator(selector).click()
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def double_click_element(self, selector: str) -> None:
        """Double-click an element."""
        self.page.locator(selector).double_click()

    def right_click_element(self, selector: str) -> None:
        """Right-click an element."""
        self.page.locator(selector).click(button="right")

    def hover_element(self, selector: str) -> None:
        """Hover over an element."""
        self.page.locator(selector).hover()

    def fill_input(self, selector: str, value: str) -> None:
        """Fill input field with value."""
        locator = self.page.locator(selector)
        locator.fill(value)


    # ============================================================================
    # Assertion Methods
    # ============================================================================

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is visible."""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False

    def element_count(self, selector: str) -> int:
        """Get count of elements matching selector."""
        return self.page.locator(selector).count()

    def get_element_text(self, selector: str) -> str:
        """Get text content of element."""
        return self.page.locator(selector).text_content()

    def get_input_value(self, selector: str) -> str:
        """Get value of input field."""
        return self.page.locator(selector).input_value()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of element."""
        return self.page.locator(selector).get_attribute(attribute)

    def is_element_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is hidden."""
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=timeout)
            return True
        except:
            return False

    def is_element_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        return self.page.locator(selector).is_enabled()

    def is_element_disabled(self, selector: str) -> bool:
        """Check if element is disabled."""
        return not self.page.locator(selector).is_enabled()

    def is_element_checked(self, selector: str) -> bool:
        """Check if checkbox/radio is checked."""
        return self.page.locator(selector).is_checked()

    def is_text_visible(self, text: str) -> bool:
        """Check if text is visible on page."""
        try:
            self.page.locator(f"text={text}").wait_for(state="visible", timeout=3000)
            return True
        except:
            return False



    # ============================================================================
    # Table Operations
    # ============================================================================

    def get_table_rows(self, table_selector: str) -> List[Locator]:
        """Get all rows in a table."""
        return self.page.locator(f"{table_selector} tbody tr").all()

    def get_table_row_count(self, table_selector: str) -> int:
        """Get number of rows in table."""
        return self.page.locator(f"{table_selector} tbody tr").count()

    def get_table_cell_text(self, table_selector: str, row: int, col: int) -> str:
        """Get text of specific table cell."""
        rows = self.get_table_rows(table_selector)
        if row < len(rows):
            cells = rows[row].locator("td").all()
            if col < len(cells):
                return cells[col].text_content()
        return ""

    def get_table_column_values(self, table_selector: str, col: int) -> List[str]:
        """Get all values in a table column."""
        rows = self.get_table_rows(table_selector)
        values = []
        for row in rows:
            cells = row.locator("td").all()
            if col < len(cells):
                values.append(cells[col].text_content().strip())
        return values

    # ============================================================================
    # Form Operations
    # ============================================================================

    def fill_form(self, form_data: Dict[str, str]) -> None:
        """Fill multiple form fields at once."""
        for selector, value in form_data.items():
            self.fill_input(selector, value)

    def submit_form(self, selector: str = "form") -> None:
        """Submit a form."""
        self.page.locator(selector).locator("button[type='submit']").click()
        self.page.wait_for_load_state("networkidle")

    def get_form_errors(self) -> List[str]:
        """Get list of form error messages."""
        errors = []
        error_elements = self.page.locator(".error, .invalid, [role='alert']").all()
        for elem in error_elements:
            error_text = elem.text_content()
            if error_text:
                errors.append(error_text.strip())
        return errors

    def form_has_errors(self) -> bool:
        """Check if form has any error messages."""
        return len(self.get_form_errors()) > 0

    # ============================================================================
    # File Operations
    # ============================================================================

    # def upload_file(self, selector: str, file_path: str) -> None:
    #     """Upload a file to file input."""
    #     self.page.locator(selector).set_input_files(file_path)
    #
    # def upload_files(self, selector: str, file_paths: List[str]) -> None:
    #     """Upload multiple files."""
    #     self.page.locator(selector).set_input_files(file_paths)

    # ============================================================================
    # Waiting Methods
    # ============================================================================

    def wait_for_element(self, selector: str, timeout: int = 5000) -> None:
        """Wait for element to appear."""
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    def wait_for_element_to_disappear(self, selector: str, timeout: int = 5000) -> None:
        """Wait for element to disappear."""
        self.page.locator(selector).wait_for(state="hidden", timeout=timeout)

    def wait_for_text(self, text: str, timeout: int = 5000) -> None:
        """Wait for specific text to appear."""
        self.page.locator(f"text={text}").wait_for(state="visible", timeout=timeout)

    def wait_for_text_to_disappear(self, text: str, timeout: int = 5000) -> None:
        """Wait for specific text to disappear."""
        self.page.locator(f"text={text}").wait_for(state="hidden", timeout=timeout)

    def wait(self, seconds: float) -> None:
        """Wait for specified seconds."""
        time.sleep(seconds)

    # ============================================================================
    # Page Information Methods
    # ============================================================================

    def get_current_url(self) -> str:
        """Get current page URL."""
        return self.page.url

    def get_page_title(self) -> str:
        """Get page title."""
        return self.page.title()

    def get_page_text(self) -> str:
        """Get all text content on page."""
        return self.page.content()

    # ============================================================================
    # Screenshot and Debug Methods
    # ============================================================================

    def take_screenshot(self, filename: str = "screenshot.png") -> None:
        """Take a screenshot of current page."""
        self.page.screenshot(path=filename)

    def print_page_content(self) -> None:
        """Print page content to console (useful for debugging)."""
        print(self.page.content())

    def get_console_logs(self) -> List[str]:
        """Get console log messages."""
        logs = []
        def on_console(msg):
            logs.append(msg.text)
        self.page.on("console", on_console)
        return logs


    def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        """Type text into an element with optional delay."""
        self.page.locator(selector).type(text, delay=delay)

    def clear_input(self, selector: str) -> None:
        """Clear an input field."""
        locator = self.page.locator(selector)
        locator.fill("")

    def select_option(self, selector: str, value: str) -> None:
        """Select an option in a dropdown."""
        self.page.locator(selector).select_option(value)

    def select_option_by_text(self, selector: str, text: str) -> None:
        """Select an option by visible text."""
        self.page.locator(selector).select_option(label=text)

    def check_checkbox(self, selector: str) -> None:
        """Check a checkbox."""
        self.page.locator(selector).check()

    def uncheck_checkbox(self, selector: str) -> None:
        """Uncheck a checkbox."""
        self.page.locator(selector).uncheck()

    def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        self.page.keyboard.press(key)

    def press_key_in_element(self, selector: str, key: str) -> None:
        """Press a key in a specific element."""
        self.page.locator(selector).press(key)

    def wait_for_url(self, url_pattern: str, timeout: int = 5000) -> None:
        """Wait for the page URL to match a pattern."""
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        """Wait for page to reach a specific load state."""
        self.page.wait_for_load_state(state)

    def go_back(self) -> None:
        """Go back to previous page."""
        self.page.go_back()

    def reload_page(self) -> None:
        """Reload current page."""
        self.page.reload()
