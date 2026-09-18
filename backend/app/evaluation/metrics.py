def summarize(results:list[dict])->dict:
    total=len(results); passed=sum(bool(r["passed"]) for r in results)
    return {"cases":total,"passed":passed,"failed":total-passed,"pass_rate":round(passed/total,4) if total else 0.0}
