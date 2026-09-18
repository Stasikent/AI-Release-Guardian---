from types import SimpleNamespace
from app.rag.hybrid import hybrid_retrieve
def test_hybrid_retrieval_returns_chunk_citation():
    docs=[
      SimpleNamespace(id=1,title="Checkout acceptance criteria",source="spec.md",content=("General notes. "*100)+"Payment submit button must remain enabled after address validation."),
      SimpleNamespace(id=2,title="Brand guide",source="brand.md",content="Typography logo colors spacing."),
    ]
    result=hybrid_retrieve("payment submit button validation",docs)
    assert result[0].document_id==1
    assert "#chunk-" in result[0].source
