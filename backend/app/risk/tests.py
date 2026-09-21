from app.models.diff import RegressionFocusItem, RegressionTestCase

def _steps(item:RegressionFocusItem)->tuple[list[str],list[str]]:
    reason=item.reason.lower()
    if "disabled" in reason or "required" in reason or "readonly" in reason:
        return (
            [f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Verify its current state.","Perform the primary interaction or submit the surrounding form."],
            ["The element state matches the intended release behavior.","The primary flow completes without unexpected blocking or validation errors."]
        )
    if "href" in reason or "src" in reason:
        return (
            [f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Activate the element or load its resource.","Observe the destination or resource response."],
            ["The target resolves to the intended destination/resource.","The related user flow remains functional."]
        )
    if "aria_" in reason or "role" in reason:
        return (
            [f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Navigate to it using the keyboard.","Inspect its accessible role/name/state and activate it when applicable."],
            ["Keyboard interaction remains usable.","Accessible semantics match the element's visible state and behavior."]
        )
    if "removed" in reason:
        return (
            ["Open the affected page.",f"Confirm that {item.locator} is absent.","Exercise the user flow that previously depended on this element."],
            ["The removal is intentional and no required action is lost.","Dependent flows complete without broken navigation or interaction."]
        )
    if "added" in reason:
        return (
            [f"Open the page containing {item.target}.",f"Locate the new element using {item.locator}.","Perform its primary interaction.","Continue the surrounding user flow."],
            ["The new element behaves as intended.","Existing surrounding behavior remains functional."]
        )
    return (
        [f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Exercise its primary user interaction.","Observe the resulting UI state."],
        ["The changed element behaves as intended.","The surrounding regression flow remains functional."]
    )

def build_regression_tests(items:list[RegressionFocusItem])->list[RegressionTestCase]:
    tests=[]
    for item in items:
        steps,expected=_steps(item)
        tests.append(RegressionTestCase(
            id=f"RG-{item.priority:03d}",priority=item.priority,severity=item.severity,
            title=f"Regression check: {item.target}",target=item.target,locator=item.locator,
            preconditions=["Target environment is available.","Baseline/current comparison has completed."],
            steps=steps,expected_results=expected,risk_points=item.risk_points,
        ))
    return tests
