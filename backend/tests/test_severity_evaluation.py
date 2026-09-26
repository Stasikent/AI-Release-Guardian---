from app.evaluation.severity import evaluate_severity

def test_severity_benchmark_reports_confusion_matrix():
    result=evaluate_severity()
    assert result["cases"]>=10
    assert 0<=result["accuracy"]<=1
    assert set(result["confusion_matrix"])=={"LOW","MEDIUM","HIGH","CRITICAL"}
