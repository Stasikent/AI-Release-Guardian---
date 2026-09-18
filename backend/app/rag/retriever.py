import math
import re
from collections import Counter
from app.models.knowledge import RetrievedContext

TOKEN_RE=re.compile(r"[A-Za-zА-Яа-я0-9_]{2,}")

def tokens(text:str)->list[str]:
    return [x.lower() for x in TOKEN_RE.findall(text)]

def score(query:str,text:str)->float:
    q=Counter(tokens(query)); d=Counter(tokens(text))
    if not q or not d: return 0.0
    dot=sum(q[t]*d[t] for t in q)
    nq=math.sqrt(sum(v*v for v in q.values()))
    nd=math.sqrt(sum(v*v for v in d.values()))
    return dot/(nq*nd) if nq and nd else 0.0

def retrieve(query:str,documents:list,limit:int=5)->list[RetrievedContext]:
    ranked=[]
    for doc in documents:
        value=score(query,f"{doc.title} {doc.content}")
        if value>0:
            excerpt=doc.content[:1200]
            ranked.append(RetrievedContext(document_id=doc.id,title=doc.title,source=doc.source,excerpt=excerpt,score=round(value,4)))
    return sorted(ranked,key=lambda x:x.score,reverse=True)[:limit]
