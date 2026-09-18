from app.evaluation.mutations import MutationCase

def _case(name,b,c,a=0,r=0,ch=0,risk=0):
    return MutationCase(name,b,c,a,r,ch,risk)

EXTENDED_CASES=[
_case("button_disabled",'<button id="pay">Pay</button>','<button id="pay" disabled>Pay</button>',0,0,0,0),
_case("button_type_changed",'<button id="save" type="button">Save</button>','<button id="save" type="submit">Save</button>',0,0,1,1),
_case("input_placeholder_changed",'<input id="email" placeholder="Email">','<input id="email" placeholder="Work email">',0,0,1,1),
_case("input_type_changed",'<input id="phone" type="text">','<input id="phone" type="tel">',0,0,1,1),
_case("input_removed",'<input id="coupon">','',0,1,0,10),
_case("textarea_added",'<form id="f"></form>','<form id="f"><textarea id="note"></textarea></form>',1,0,0,1),
_case("select_removed",'<select id="country"><option>DE</option></select>','',0,1,0,10),
_case("form_added",'','<form id="signup"></form>',1,0,0,1),
_case("form_removed",'<form id="signup"></form>','',0,1,0,10),
_case("aria_label_changed",'<button id="menu" aria-label="Open menu"></button>','<button id="menu" aria-label="Menu"></button>',0,0,0,0),
_case("title_changed",'<a id="docs" title="Docs" href="/docs">Docs</a>','<a id="docs" title="Documentation" href="/docs">Docs</a>',0,0,1,1),
_case("image_src_changed",'<img id="hero" src="/a.png">','<img id="hero" src="/b.png">',0,0,1,1),
_case("image_added",'','<img id="logo" src="/logo.png">',1,0,0,0),
_case("table_removed",'<table id="orders"></table>','',0,1,0,1),
_case("link_added",'','<a id="pricing" href="/pricing">Pricing</a>',1,0,0,1),
_case("link_removed",'<a id="logout" href="/logout">Logout</a>','',0,1,0,10),
_case("link_text_changed",'<a id="home" href="/">Home</a>','<a id="home" href="/">Dashboard</a>',0,0,1,1),
_case("class_changed",'<button id="cta" class="primary">Go</button>','<button id="cta" class="danger">Go</button>',0,0,1,1),
_case("value_changed",'<input id="qty" value="1">','<input id="qty" value="2">',0,0,1,1),
_case("name_identity_stable",'<input name="search" placeholder="Search">','<input name="search" placeholder="Find">',0,0,1,1),
_case("id_identity_stable",'<button id="next">Next</button>','<button id="next">Continue</button>',0,0,1,1),
_case("two_buttons_one_changed",'<button id="a">A</button><button id="b">B</button>','<button id="a">A</button><button id="b">Bee</button>',0,0,1,1),
_case("one_of_two_removed",'<input id="a"><input id="b">','<input id="a">',0,1,0,10),
_case("one_of_two_added",'<input id="a">','<input id="a"><input id="b">',1,0,0,1),
_case("multiple_changes",'<button id="buy">Buy</button><input id="coupon">','<button id="buy">Pay</button><a id="help" href="/help">Help</a>',1,1,1,10),
_case("semantic_container_noise",'<div><button id="ok">OK</button></div>','<section><button id="ok">OK</button></section>',0,0,0,0),
_case("unsupported_div_change",'<div id="message">Old</div>','<div id="message">New</div>',0,0,0,0),
_case("order_change",'<button id="a">A</button><button id="b">B</button>','<button id="b">B</button><button id="a">A</button>',0,0,0,0),
_case("href_query_changed",'<a id="report" href="/report?v=1">Report</a>','<a id="report" href="/report?v=2">Report</a>',0,0,1,1),
_case("textarea_text_changed",'<textarea id="bio">old</textarea>','<textarea id="bio">new</textarea>',0,0,1,1),
]
