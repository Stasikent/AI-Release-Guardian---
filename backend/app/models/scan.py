from pydantic import BaseModel, Field, HttpUrl

class ScanRequest(BaseModel):
    url: HttpUrl
    wait_until: str = Field(default="networkidle", pattern="^(load|domcontentloaded|networkidle|commit)$")
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)

class TestableObject(BaseModel):
    index: int
    object_type: str
    tag_name: str = ""
    id: str = ""
    name: str = ""
    type: str = ""
    css_class: str = ""
    placeholder: str = ""
    value: str = ""
    text: str = ""
    aria_label: str = ""
    title: str = ""
    href: str = ""
    src: str = ""
    locator: str = ""
    display_name: str = ""

class ScanResult(BaseModel):
    url: str
    title: str = ""
    total_testable_objects: int
    object_counts: dict[str, int]
    testable_objects: list[TestableObject]
