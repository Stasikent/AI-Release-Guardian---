from dataclasses import dataclass
from types import SimpleNamespace
from app.rag.hybrid import hybrid_retrieve

@dataclass(frozen=True)
class RetrievalCase:
    query:str
    expected_document_id:int

DOCUMENTS=[
 SimpleNamespace(id=1,title="Checkout requirements",source="checkout.md",content="Payment submit button must remain available after address validation. Coupon field is optional."),
 SimpleNamespace(id=2,title="Authentication",source="auth.md",content="Login requires email and password. Password reset link must remain visible."),
 SimpleNamespace(id=3,title="Navigation",source="nav.md",content="Help link routes to support center. Main navigation includes pricing and dashboard."),
 SimpleNamespace(id=4,title="Brand",source="brand.md",content="Logo typography spacing and hero image guidelines."),
 SimpleNamespace(id=5,title="Orders",source="orders.md",content="Orders table displays order history and report download links."),
]
CASES=[
 RetrievalCase("payment submit button address validation",1),
 RetrievalCase("coupon checkout field",1),
 RetrievalCase("login email password",2),
 RetrievalCase("password reset link",2),
 RetrievalCase("help support navigation",3),
 RetrievalCase("pricing dashboard navigation",3),
 RetrievalCase("logo typography hero image",4),
 RetrievalCase("orders table history",5),
 RetrievalCase("report download orders",5),
]

def evaluate_retrieval()->dict:
    reciprocal=[]; hits=0; rows=[]
    for case in CASES:
        result=hybrid_retrieve(case.query,DOCUMENTS,limit=3)
        ids=[x.document_id for x in result]
        rank=ids.index(case.expected_document_id)+1 if case.expected_document_id in ids else None
        if rank: hits+=1; reciprocal.append(1/rank)
        else: reciprocal.append(0)
        rows.append({"query":case.query,"expected":case.expected_document_id,"rank":rank,"top3":ids})
    n=len(CASES)
    return {"cases":n,"hit_at_3":round(hits/n,4),"mrr":round(sum(reciprocal)/n,4),"results":rows}
