from app.models.diff import RegressionFocusItem, RegressionTestCase

def _steps(item:RegressionFocusItem)->tuple[list[str],list[str]]:
    reason=item.reason.lower()
    if any(x in reason for x in ("disabled","required","readonly","checked","selected")):
        return ([f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Inspect its current interaction state.","Execute its primary user interaction."],["The element state matches the intended release behavior.","The primary interaction completes without an unexpected block or validation regression."])
    if "href" in reason or "src" in reason:
        return ([f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Activate the element or load its resource.","Verify the resulting destination/resource."],["The target resolves to the intended destination/resource.","The related user flow remains functional."])
    if "aria_" in reason or "role" in reason:
        return ([f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Navigate to it with the keyboard.","Inspect its exposed accessibility role/state and operate it."],["Keyboard interaction remains usable.","The exposed accessibility role/state matches the element behavior."])
    return ([f"Open the page containing {item.target}.",f"Locate the element using {item.locator}.","Exercise the element in its primary user flow."],["The changed element behaves as intended.","The surrounding user flow completes without regression."])

def build_regression_tests(focus:list[RegressionFocusItem])->list[RegressionTestCase]:
    tests=[]
    for item in focus:
        steps,expected=_steps(item)
        tests.append(RegressionTestCase(id=f"REG-{item.priority:03d}",priority=item.priority,severity=item.severity,title=f"Regression check: {item.target}",target=item.target,locator=item.locator,preconditions=["Target page is reachable and the test user/session is ready."],steps=steps,expected_results=expected,risk_points=item.risk_points))
    return tests
