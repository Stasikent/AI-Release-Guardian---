import hashlib
from collections import defaultdict
from app.models.diff import DiffReport, ElementChange
from app.models.scan import TestableObject

IDENTITY_FIELDS = ("object_type", "id", "name", "aria_label", "href", "src")
COMPARE_FIELDS = ("type", "css_class", "placeholder", "value", "text", "title", "href", "src")

def fingerprint(obj: TestableObject) -> str:
    strong = "|".join([
        obj.object_type,
        obj.id or obj.name or obj.aria_label or obj.href or obj.src or obj.locator,
    ])
    return hashlib.sha256(strong.encode("utf-8")).hexdigest()[:16]

def _bucket(objects: list[TestableObject]) -> dict[str, list[TestableObject]]:
    buckets: dict[str, list[TestableObject]] = defaultdict(list)
    for obj in objects:
        buckets[fingerprint(obj)].append(obj)
    return buckets

def compare_objects(
    baseline: list[TestableObject], current: list[TestableObject]
) -> DiffReport:
    old = _bucket(baseline)
    new = _bucket(current)
    added: list[TestableObject] = []
    removed: list[TestableObject] = []
    changed: list[ElementChange] = []
    unchanged = 0

    for fp in sorted(set(old) | set(new)):
        old_items = old.get(fp, [])
        new_items = new.get(fp, [])
        paired = min(len(old_items), len(new_items))

        for i in range(paired):
            before, after = old_items[i], new_items[i]
            fields = [
                field for field in COMPARE_FIELDS
                if getattr(before, field) != getattr(after, field)
            ]
            if fields:
                changed.append(ElementChange(
                    fingerprint=fp,
                    before=before,
                    after=after,
                    changed_fields=fields,
                ))
            else:
                unchanged += 1

        removed.extend(old_items[paired:])
        added.extend(new_items[paired:])

    return DiffReport(
        added=added,
        removed=removed,
        changed=changed,
        unchanged_count=unchanged,
    )
