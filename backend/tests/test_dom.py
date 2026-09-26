from app.analyzers.dom import count_by_type, extract_testable_objects

HTML = """
<html><body>
<form id="login-form">
  <input id="email" name="email" type="email" placeholder="Email">
  <button aria-label="Sign in">Login</button>
</form>
<a href="/help">Help</a>
<img src="/logo.png" alt="Logo">
</body></html>
"""

def test_extract_testable_objects() -> None:
    objects = extract_testable_objects(HTML)
    counts = count_by_type(objects)
    assert counts == {"button": 1, "form": 1, "image": 1, "input": 1, "link": 1}
    email = next(obj for obj in objects if obj.object_type == "input")
    assert email.locator == "#email"
    assert email.display_name == "email"

def test_aria_label_has_priority_for_display_name() -> None:
    objects = extract_testable_objects(HTML)
    button = next(obj for obj in objects if obj.object_type == "button")
    assert button.display_name == "Sign in"

def test_extracts_interactive_and_accessibility_state() -> None:
    html='<input id="tos" type="checkbox" required checked aria-describedby="hint"><button id="menu" disabled aria-expanded="false">Menu</button>'
    objects=extract_testable_objects(html)
    checkbox=next(x for x in objects if x.id=="tos")
    button=next(x for x in objects if x.id=="menu")
    assert checkbox.required is True and checkbox.checked is True
    assert checkbox.aria_describedby=="hint"
    assert button.disabled is True and button.aria_expanded=="false"
