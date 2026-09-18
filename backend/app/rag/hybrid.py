import math
from collections import Counter
from app.models.knowledge import RetrievedContext
from app.rag.chunking import chunk_text
from app.rag.retriever import tokens

def _cosine(a:Counter,b:Counter)->float:
    if not a or not b:return 0.0
    dot=sum(a[t]*b[t] for t in a)
    na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0

def _coverage(query:list[str],document:list[str])->float:
    q=set(query)
    return len(q & set(document))/len(q) if q else 0.0

def hybrid_retrieve(query:str,documents:list,limit:int=5)->list[RetrievedContext]:
    q=tokens(query); qc=Counter(q); candidates=[]
    for doc in documents:
        for chunk in chunk_text(doc.content):
            dt=tokens(f"{doc.title} {chunk.text}")
            lexical=_cosine(qc,Counter(dt))
            coverage=_coverage(q,dt)
            title_bonus=0.15*_coverage(q,tokens(doc.title))
            score=0.65*lexical+0.35*coverage+title_bonus
            if score>0:
                candidates.append(RetrievedContext(document_id=doc.id,title=doc.title,source=f"{doc.source}#chunk-{chunk.index}",excerpt=chunk.text,score=round(score,4)))
    candidates.sort(key=lambda x:x.score,reverse=True)
    result=[]; seen=set()
    for item in candidates:
        key=(item.document_id,item.excerpt)
        if key not in seen: result.append(item); seen.add(key)
        if len(result)>=limit: break
    return result
