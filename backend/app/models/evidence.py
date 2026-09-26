from pydantic import BaseModel,Field

class EvidenceItem(BaseModel):
    id:str
    kind:str
    statement:str
    source:str
    score:float|None=None

class EvidenceBundle(BaseModel):
    observed:list[EvidenceItem]=Field(default_factory=list)
    retrieved:list[EvidenceItem]=Field(default_factory=list)
