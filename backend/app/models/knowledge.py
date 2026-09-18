from pydantic import BaseModel, Field

class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(min_length=2,max_length=200)
    source: str = Field(default="manual",max_length=500)
    content: str = Field(min_length=10,max_length=100000)

class KnowledgeDocumentRead(BaseModel):
    id: int
    project_id: int
    title: str
    source: str

class RetrievedContext(BaseModel):
    document_id: int
    title: str
    source: str
    excerpt: str
    score: float
