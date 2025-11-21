"""
Page Factory for dynamically importing and instantiating page objects.
Provides flexible mechanism to load page classes without hardcoding imports.

Extended: Includes a Builder Pattern implementation for form filling.
This lets tests build form objects via a fluent builder API or from a dict
and apply `form.fill(page_obj)` to populate forms using the Page Objects (BasePage API).
"""

import importlib
from typing import Type, Any, Optional, List, Dict, Callable
from pathlib import Path


class PageFactory:
    """
    Factory class to dynamically import and instantiate page objects.
    
    Supports:
    - Dynamic import of page modules
    - Automatic page class discovery
    - Caching of imported modules
    - Error handling for missing pages
    """

    # Cache for imported modules to avoid repeated imports
    _module_cache = {}

    # Base path for page objects
    PAGES_DIR = Path(__file__).parent

    # Mapping of page names to module and class names
    PAGES_MAPPING = {
        "home": ("home_page", "HomePage"),
        "members": ("members_page", "MembersPage"),
        "members_list": ("members_page", "MembersPage"),
        "addmember": ("addmember_page", "AddMemberPage"),
        "update_member": ("update_member_page", "UpdateMemberPage"),
        "member_detail": ("member_detail_page", "MemberDetailPage"),
        "courses": ("courses_page", "CoursesPage"),
        "add_course": ("add_course_page", "AddCoursePage"),
        "update_course": ("update_course_page", "UpdateCoursePage"),
        "course_detail": ("course_detail_page", "CourseDetailPage"),
    }

    @classmethod
    def get_page(cls, page_name: str, playwright_page: Any, base_url: str = "http://127.0.0.1:8000") -> Any:
        """
        Get an instance of a page object by name.
        """
        page_name = page_name.lower().strip()
        
        # Check if page is in mapping
        if page_name not in cls.PAGES_MAPPING:
            raise ValueError(
                f"Page '{page_name}' not found in mapping. "
                f"Available pages: {', '.join(cls.PAGES_MAPPING.keys())}"
            )
        
        module_name, class_name = cls.PAGES_MAPPING[page_name]
        
        try:
            # Get or import module
            module = cls._get_module(module_name)
            
            # Get class from module
            if not hasattr(module, class_name):
                raise AttributeError(
                    f"Class '{class_name}' not found in module '{module_name}'. "
                    f"Available classes: {[name for name in dir(module) if not name.startswith('_')]}"
                )
            
            page_class = getattr(module, class_name)
            
            # Instantiate and return
            return page_class(playwright_page, base_url)
            
        except ImportError as e:
            raise ImportError(
                f"Could not import page module '{module_name}' for page '{page_name}'. "
                f"Error: {str(e)}"
            )

    @classmethod
    def _get_module(cls, module_name: str) -> Any:
        """
        Get or import a module from the pages directory.
        Uses caching to avoid repeated imports.
        """
        # Check cache first
        if module_name in cls._module_cache:
            return cls._module_cache[module_name]
        
        # Import module
        full_module_name = f"tests.ui.pages.{module_name}"
        module = importlib.import_module(full_module_name)
        
        # Cache it
        cls._module_cache[module_name] = module
        
        return module

    @classmethod
    def get_available_pages(cls) -> list:
        """Get list of all available page names."""
        return sorted(cls.PAGES_MAPPING.keys())

    @classmethod
    def register_page(cls, page_name: str, module_name: str, class_name: str) -> None:
        """Register a new page to the factory."""
        cls.PAGES_MAPPING[page_name.lower()] = (module_name, class_name)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the module cache. Useful for testing and reloading."""
        cls._module_cache.clear()

    @classmethod
    def print_mapping(cls) -> None:
        """Print all registered pages to console."""
        print("\n" + "="*60)
        print("Page Factory Mapping")
        print("="*60)
        for page_name, (module_name, class_name) in sorted(cls.PAGES_MAPPING.items()):
            print(f"  {page_name:20} -> {module_name}.{class_name}")
        print("="*60 + "\n")


# ----------------------------------------------------------------------------
# Builder Pattern for Form Filling
# ----------------------------------------------------------------------------

class Field:
    """Represents a single form field (product part).

    usage:
        f = Field(name="first_name", selector="[name='first_name']", value="Alice", field_type="text")
        f.fill(page_obj)
    """

    def __init__(self, name: str, selector: str, value: Any = None, field_type: str = "text", options: Optional[Dict[str, Any]] = None):
        self.name = name
        self.selector = selector
        self.value = value
        self.field_type = field_type
        self.options = options or {}

    def fill(self, page_obj: Any) -> None:
        """Fill this field on the provided page object using BasePage methods."""
        if self.value is None:
            return

        # Text inputs and textareas
        if self.field_type in ("text", "textarea"):
            try:
                page_obj.fill_input(self.selector, str(self.value))
            except Exception:
                page_obj.type_text(self.selector, str(self.value))
            return

        # Select/dropdown
        if self.field_type == "select":
            if self.options.get("by_value"):
                try:
                    page_obj.select_option(self.selector, str(self.value))
                except Exception:
                    page_obj.select_option_by_text(self.selector, str(self.value))
            else:
                page_obj.select_option_by_text(self.selector, str(self.value))
            return

        # File upload
        if self.field_type == "file":
            page_obj.upload_file(self.selector, str(self.value))
            return

        # Checkbox
        if self.field_type == "checkbox":
            boolean_value = bool(self.value)
            if boolean_value:
                try:
                    page_obj.check_checkbox(self.selector)
                except Exception:
                    page_obj.click_element(self.selector)
            else:
                try:
                    page_obj.uncheck_checkbox(self.selector)
                except Exception:
                    page_obj.click_element(self.selector)
            return

        # Radio
        if self.field_type == "radio":
            try:
                page_obj.click_element(self.selector)
            except Exception:
                raise

        # Fallback: fill as text
        page_obj.fill_input(self.selector, str(self.value))

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "selector": self.selector, "value": self.value, "type": self.field_type}


class Form:
    """Product representing a collection of Fields.

    Provides `add_field` and `fill(page_obj)` methods.
    """

    def __init__(self, name: str = "form"):
        self.name = name
        self._fields: List[Field] = []

    def add_field(self, field: Field) -> "Form":
        self._fields.append(field)
        return self

    def add_fields(self, fields: List[Field]) -> "Form":
        for f in fields:
            self.add_field(f)
        return self

    def fill(self, page_obj: Any) -> None:
        for field in self._fields:
            field.fill(page_obj)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "fields": [f.to_dict() for f in self._fields]}

    def find(self, name: str) -> Optional[Field]:
        for f in self._fields:
            if f.name == name:
                return f
        return None


class FormBuilder:
    """Fluent builder for creating Form instances.

    Example fluent usage:
        form = (
            FormBuilder("member")
            .add_text("first_name", "[name='first_name']", "John")
            .add_text("last_name", "[name='last_name']", "Doe")
            .add_file("image", "input[type='file']", "tests/fixtures/avatar.png")
            .build()
        )

    Or build from dict spec using `from_dict`.
    """

    def __init__(self, name: str = "form"):
        self._form = Form(name=name)

    def add_text(self, name: str, selector: str, value: Any) -> "FormBuilder":
        self._form.add_field(Field(name=name, selector=selector, value=value, field_type="text"))
        return self

    def add_textarea(self, name: str, selector: str, value: Any) -> "FormBuilder":
        self._form.add_field(Field(name=name, selector=selector, value=value, field_type="textarea"))
        return self

    def add_select(self, name: str, selector: str, value: Any, by_value: bool = False) -> "FormBuilder":
        self._form.add_field(Field(name=name, selector=selector, value=value, field_type="select", options={"by_value": by_value}))
        return self

    def add_file(self, name: str, selector: str, file_path: str) -> "FormBuilder":
        self._form.add_field(Field(name=name, selector=selector, value=file_path, field_type="file"))
        return self

    def add_checkbox(self, name: str, selector: str, checked: bool) -> "FormBuilder":
        self._form.add_field(Field(name=name, selector=selector, value=checked, field_type="checkbox"))
        return self

    def add_radio(self, name: str, selector: str, value: Any) -> "FormBuilder":
        self._form.add_field(Field(name=name, selector=selector, value=value, field_type="radio"))
        return self

    def add_custom(self, field: Field) -> "FormBuilder":
        self._form.add_field(field)
        return self

    def build(self) -> Form:
        return self._form

    @staticmethod
    def from_dict(spec: Dict[str, Any], name: str = "form") -> Form:
        """Create a Form from a declarative dict spec.

        Spec format example:
        {
            "first_name": {"selector": "[name='first_name']", "value": "John", "type": "text"},
            "last_name": {"selector": "[name='last_name']", "value": "Doe", "type": "text"},
            "image": {"selector": "input[type='file']", "value": "tests/fixtures/avatar.png", "type": "file"},
            "contact": {"_type": "group", "fields": {
                "email": {"selector": "[name='email']", "value": "john@example.com", "type": "text"}
            }}
        }

        Nested groups are flattened into fields prefixed by group name.
        """
        builder = FormBuilder(name)

        def _walk(prefix: str, d: Dict[str, Any]):
            for key, desc in d.items():
                if isinstance(desc, dict) and desc.get("_type") == "group":
                    fields = desc.get("fields", {})
                    _walk(f"{prefix}{key}_", fields)
                    continue
                selector = desc.get("selector") or desc.get("locator")
                value = desc.get("value")
                field_type = desc.get("type", "text")
                options = desc.get("options", None)
                full_name = f"{prefix}{key}" if prefix else key
                if field_type == "text":
                    builder.add_text(full_name, selector, value)
                elif field_type == "textarea":
                    builder.add_textarea(full_name, selector, value)
                elif field_type == "select":
                    by_value = (options or {}).get("by_value", False)
                    builder.add_select(full_name, selector, value, by_value)
                elif field_type == "file":
                    builder.add_file(full_name, selector, value)
                elif field_type == "checkbox":
                    builder.add_checkbox(full_name, selector, bool(value))
                elif field_type == "radio":
                    builder.add_radio(full_name, selector, value)
                else:
                    # fallback to text
                    builder.add_text(full_name, selector, value)

        _walk("", spec)
        return builder.build()


# ----------------------------------------------------------------------------
# Usage examples (in comments):
# ----------------------------------------------------------------------------
#
# # Fluent builder usage:
# form = (
#     FormBuilder("member")
#     .add_text("first_name", "[name='first_name']", "Alice")
#     .add_text("last_name", "[name='last_name']", "Smith")
#     .add_file("photo", "input[type='file']", "/tmp/photo.png")
#     .build()
# )
#
# # Fill the form using a Page Object that implements BasePage API:
# members_add = PageFactory.get_page("add_member", playwright_page)
# form.fill(members_add)
#
# # Build from dict spec:
# spec = {
#     "first_name": {"selector": "[name='first_name']", "value": "John", "type": "text"},
#     "last_name": {"selector": "[name='last_name']", "value": "Doe", "type": "text"},
#     "image": {"selector": "input[type='file']", "value": "tests/fixtures/avatar.png", "type": "file"},
#     "contact": {"_type": "group", "fields": {
#         "email": {"selector": "[name='email']", "value": "john@example.com", "type": "text"},
#     }}
# }
# form = FormBuilder.from_dict(spec)
# form.fill(members_add)
#
# ----------------------------------------------------------------------------
