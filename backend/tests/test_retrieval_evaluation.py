from app.evaluation.retrieval import evaluate_retrieval
def test_retrieval_benchmark_has_metrics():
    result=evaluate_retrieval()
    assert result["cases"]>=8
    assert 0<=result["hit_at_3"]<=1
    assert 0<=result["mrr"]<=1
