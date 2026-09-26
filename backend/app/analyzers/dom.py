from collections import Counter
from bs4 import BeautifulSoup, Tag
from app.models.scan import TestableObject

SUPPORTED_SELECTORS=(("input","input"),("button","button"),("form","form"),("link","a"),("select","select"),("textarea","textarea"),("table","table"),("image","img"))

def _normalize(value):
    if value is None:return ""
    if isinstance(value,list):value=" ".join(str(x) for x in value)
    return " ".join(str(value).split()).strip()
def _attr(tag,name):return _normalize(tag.attrs.get(name,""))
def _bool_attr(tag,name):return tag.has_attr(name)
def _locator(tag):
    if _attr(tag,"id"):return f'#{_attr(tag,"id")}'
    if _attr(tag,"name"):return f'{tag.name}[name="{_attr(tag,"name")}"]'
    if _attr(tag,"aria-label"):return f'{tag.name}[aria-label="{_attr(tag,"aria-label").replace(chr(34),chr(92)+chr(34))}"]'
    return tag.name
def _display_name(obj):
    for value in (obj.aria_label,obj.name,obj.id,obj.placeholder,obj.text,obj.title,obj.locator):
        if value:return value
    return f"{obj.object_type}_{obj.index}"

def extract_testable_objects(html):
    soup=BeautifulSoup(html,"html.parser");objects=[]
    for object_type,selector in SUPPORTED_SELECTORS:
        for index,tag in enumerate(soup.find_all(selector),start=1):
            obj=TestableObject(index=index,object_type=object_type,tag_name=tag.name or "",id=_attr(tag,"id"),name=_attr(tag,"name"),type=_attr(tag,"type"),css_class=_attr(tag,"class"),placeholder=_attr(tag,"placeholder"),value=_attr(tag,"value"),text=_normalize(tag.get_text(" ",strip=True)),aria_label=_attr(tag,"aria-label"),aria_describedby=_attr(tag,"aria-describedby"),aria_expanded=_attr(tag,"aria-expanded"),aria_checked=_attr(tag,"aria-checked"),aria_selected=_attr(tag,"aria-selected"),role=_attr(tag,"role"),disabled=_bool_attr(tag,"disabled"),required=_bool_attr(tag,"required"),checked=_bool_attr(tag,"checked"),selected=_bool_attr(tag,"selected"),readonly=_bool_attr(tag,"readonly"),title=_attr(tag,"title"),href=_attr(tag,"href"),src=_attr(tag,"src"),locator=_locator(tag))
            obj.display_name=_display_name(obj);objects.append(obj)
    return objects
def count_by_type(objects):return dict(sorted(Counter(obj.object_type for obj in objects).items()))
