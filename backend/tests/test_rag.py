from types import SimpleNamespace
from app.rag.retriever import retrieve

def test_retrieval_ranks_relevant_document():
    docs=[
        SimpleNamespace(id=1,title="Checkout requirements",source="spec",content="Checkout button must remain visible and payment flow is critical."),
        SimpleNamespace(id=2,title="Brand",source="guide",content="Logo spacing and typography guidance."),
    ]
    result=retrieve("checkout payment button",docs)
    assert result[0].document_id==1
    assert result[0].score>0
