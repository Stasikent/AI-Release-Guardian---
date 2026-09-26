from app.evaluation.report import build_evaluation_report

def test_combined_evaluation_report():
    report=build_evaluation_report()
    assert report["mutation"]["cases"]>=40
    assert report["retrieval"]["cases"]>=8
    assert report["severity"]["cases"]>=10
    assert report["status"] in {"PASS","FAIL"}
