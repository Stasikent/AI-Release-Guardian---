# AI Release Guardian V2 — Evaluation

V2 includes a deterministic mutation suite before any portfolio accuracy claim is made.

## Current baseline suite
The suite injects known HTML changes and checks the expected structural diff and minimum risk response:
- button text change
- critical interactive element removal
- input addition
- link target change
- unchanged control case

Run with:

```bash
cd backend
pytest -q
```

Or inspect the API:

```
GET /api/v1/evaluation/mutations
```

## Important
A passing unit suite is not the same as production accuracy. The initial cases are controlled fixtures intended to catch regressions in the Guardian itself. Portfolio metrics should only be published after CI executes the suite and after the benchmark is expanded with realistic pages, ambiguous element identities, dynamic DOM states, and retrieval relevance labels.

Planned metrics:
- mutation detection precision/recall
- field-change classification accuracy
- risk calibration by severity labels
- retrieval Hit@K / MRR
- grounded AI citation validity
