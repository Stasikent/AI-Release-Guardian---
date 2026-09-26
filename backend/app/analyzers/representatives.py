from collections import defaultdict
from app.models.diff import RepresentativeObject
from app.models.scan import TestableObject

def choose_representatives(objects: list[TestableObject]) -> list[RepresentativeObject]:
    groups: dict[str, list[TestableObject]] = defaultdict(list)
    for obj in objects:
        groups[obj.object_type].append(obj)

    result: list[RepresentativeObject] = []
    for object_type in sorted(groups):
        candidates = groups[object_type]
        representative = max(
            candidates,
            key=lambda obj: (
                bool(obj.id) + bool(obj.name) + bool(obj.aria_label)
                + bool(obj.placeholder) + bool(obj.text),
                -obj.index,
            ),
        )
        result.append(
            RepresentativeObject(
                object_type=object_type,
                count=len(candidates),
                representative=representative,
            )
        )
    return result
