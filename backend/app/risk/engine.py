from app.models.diff import DiffReport, RiskFactor, RiskReport

INTERACTIVE_TYPES = {"input", "button", "form", "select", "textarea", "link"}

def _factor(code: str, description: str, weight: int, count: int) -> RiskFactor:
    return RiskFactor(
        code=code,
        description=description,
        weight=weight,
        count=count,
        points=weight * count,
    )

def calculate_risk(diff: DiffReport) -> RiskReport:
    removed_interactive = sum(
        obj.object_type in INTERACTIVE_TYPES for obj in diff.removed
    )
    added_interactive = sum(
        obj.object_type in INTERACTIVE_TYPES for obj in diff.added
    )
    changed_interactive = sum(
        change.after.object_type in INTERACTIVE_TYPES for change in diff.changed
    )
    locator_changes = sum(
        any(field in change.changed_fields for field in ("href", "src"))
        for change in diff.changed
    )

    factors = [
        _factor("removed_interactive", "Interactive elements removed", 12, removed_interactive),
        _factor("changed_interactive", "Interactive elements changed", 8, changed_interactive),
        _factor("added_interactive", "Interactive elements added", 4, added_interactive),
        _factor("removed_other", "Non-interactive elements removed", 4, len(diff.removed) - removed_interactive),
        _factor("changed_other", "Non-interactive elements changed", 2, len(diff.changed) - changed_interactive),
        _factor("navigation_media_change", "Navigation or resource targets changed", 5, locator_changes),
    ]
    factors = [factor for factor in factors if factor.count > 0]
    raw = sum(factor.points for factor in factors)
    score = min(raw, 100)

    if score < 15:
        level = "LOW"
    elif score < 40:
        level = "MEDIUM"
    elif score < 70:
        level = "HIGH"
    else:
        level = "CRITICAL"

    summary = (
        f"{len(diff.added)} added, {len(diff.removed)} removed, "
        f"{len(diff.changed)} changed elements; {diff.unchanged_count} unchanged."
    )
    return RiskReport(
        score=score,
        raw_score=raw,
        level=level,
        factors=factors,
        summary=summary,
    )
