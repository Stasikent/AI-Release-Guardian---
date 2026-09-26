import hashlib
from collections import defaultdict
from app.models.diff import DiffReport,ElementChange
from app.models.scan import TestableObject

COMPARE_FIELDS=("type","css_class","placeholder","value","text","aria_label","aria_describedby","aria_expanded","aria_checked","aria_selected","role","disabled","required","checked","selected","readonly","title","href","src")
def fingerprint(obj):
    strong="|".join([obj.object_type,obj.id or obj.name or obj.locator])
    return hashlib.sha256(strong.encode()).hexdigest()[:16]
def _bucket(objects):
    buckets=defaultdict(list)
    for obj in objects:buckets[fingerprint(obj)].append(obj)
    return buckets
def compare_objects(baseline,current):
    old,new=_bucket(baseline),_bucket(current);added=[];removed=[];changed=[];unchanged=0
    for fp in sorted(set(old)|set(new)):
        oi,ni=old.get(fp,[]),new.get(fp,[]);paired=min(len(oi),len(ni))
        for i in range(paired):
            before,after=oi[i],ni[i]
            fields=[f for f in COMPARE_FIELDS if getattr(before,f)!=getattr(after,f)]
            if fields:changed.append(ElementChange(fingerprint=fp,before=before,after=after,changed_fields=fields))
            else:unchanged+=1
        removed.extend(oi[paired:]);added.extend(ni[paired:])
    return DiffReport(added=added,removed=removed,changed=changed,unchanged_count=unchanged)
