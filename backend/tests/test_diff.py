from app.analyzers.diff import compare_objects
from app.models.scan import TestableObject as DomObject
from app.risk.engine import calculate_risk

def obj(index: int, kind: str, id_: str, text: str = "") -> DomObject:
    return DomObject(
        index=index, object_type=kind, tag_name=kind,
        id=id_, text=text, locator=f"#{id_}", display_name=id_,
    )

def test_compare_detects_added_removed_changed() -> None:
    baseline = [
        obj(1, "button", "save", "Save"),
        obj(2, "input", "email"),
        obj(3, "link", "help", "Help"),
    ]
    current = [
        obj(1, "button", "save", "Save changes"),
        obj(2, "input", "email"),
        obj(4, "button", "cancel", "Cancel"),
    ]
    diff = compare_objects(baseline, current)
    assert len(diff.added) == 1
    assert len(diff.removed) == 1
    assert len(diff.changed) == 1
    assert diff.unchanged_count == 1
    assert diff.changed[0].changed_fields == ["text"]

def test_risk_is_explainable() -> None:
    baseline = [obj(1, "button", "save"), obj(2, "link", "help")]
    current = [obj(1, "button", "save", "Save now")]
    risk = calculate_risk(compare_objects(baseline, current))
    assert risk.score > 0
    assert risk.level in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert any(f.code == "removed_interactive" for f in risk.factors)
