import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    index:int
    text:str

def chunk_text(text:str,max_chars:int=900,overlap_chars:int=120)->list[Chunk]:
    clean=re.sub(r"\s+"," ",text).strip()
    if not clean: return []
    chunks=[]; start=0; index=0
    while start<len(clean):
        end=min(start+max_chars,len(clean))
        if end<len(clean):
            boundary=clean.rfind(" ",start,end)
            if boundary>start+max_chars//2: end=boundary
        part=clean[start:end].strip()
        if part: chunks.append(Chunk(index=index,text=part)); index+=1
        if end>=len(clean): break
        start=max(end-overlap_chars,start+1)
    return chunks
