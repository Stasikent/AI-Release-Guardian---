from app.analyzers.representatives import choose_representatives
from app.models.scan import TestableObject as DomObject

def test_prefers_well_identified_representative() -> None:
    objects = [
        DomObject(index=1, object_type="button", tag_name="button", locator="button"),
        DomObject(index=2, object_type="button", tag_name="button", id="submit", text="Submit", locator="#submit"),
    ]
    groups = choose_representatives(objects)
    assert len(groups) == 1
    assert groups[0].count == 2
    assert groups[0].representative.id == "submit"
