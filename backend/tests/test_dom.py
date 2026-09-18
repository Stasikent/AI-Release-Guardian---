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
