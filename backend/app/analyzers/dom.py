from collections import Counter
from bs4 import BeautifulSoup, Tag

from app.models.scan import TestableObject

SUPPORTED_SELECTORS: tuple[tuple[str, str], ...] = (
    ("input", "input"),
    ("button", "button"),
    ("form", "form"),
    ("link", "a"),
    ("select", "select"),
    ("textarea", "textarea"),
    ("table", "table"),
    ("image", "img"),
)

def _normalize(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    return " ".join(str(value).split()).strip()

def _attr(tag: Tag, name: str) -> str:
    return _normalize(tag.attrs.get(name, ""))

def _locator(tag: Tag) -> str:
    element_id = _attr(tag, "id")
    if element_id:
        return f"#{element_id}"
    name = _attr(tag, "name")
    if name:
        return f'{tag.name}[name="{name}"]'
    aria = _attr(tag, "aria-label")
    if aria:
        escaped = aria.replace('"', '\\"')
        return f'{tag.name}[aria-label="{escaped}"]'
    return tag.name

def _display_name(obj: TestableObject) -> str:
    for value in (
        obj.aria_label, obj.name, obj.id, obj.placeholder,
        obj.text, obj.title, obj.locator,
    ):
        if value:
            return value
    return f"{obj.object_type}_{obj.index}"

def extract_testable_objects(html: str) -> list[TestableObject]:
    soup = BeautifulSoup(html, "html.parser")
    objects: list[TestableObject] = []

    for object_type, selector in SUPPORTED_SELECTORS:
        for index, tag in enumerate(soup.find_all(selector), start=1):
            obj = TestableObject(
                index=index,
                object_type=object_type,
                tag_name=tag.name or "",
                id=_attr(tag, "id"),
                name=_attr(tag, "name"),
                type=_attr(tag, "type"),
                css_class=_attr(tag, "class"),
                placeholder=_attr(tag, "placeholder"),
                value=_attr(tag, "value"),
                text=_normalize(tag.get_text(" ", strip=True)),
                aria_label=_attr(tag, "aria-label"),
                title=_attr(tag, "title"),
                href=_attr(tag, "href"),
                src=_attr(tag, "src"),
                locator=_locator(tag),
            )
            obj.display_name = _display_name(obj)
            objects.append(obj)
    return objects

def count_by_type(objects: list[TestableObject]) -> dict[str, int]:
    return dict(sorted(Counter(obj.object_type for obj in objects).items()))
