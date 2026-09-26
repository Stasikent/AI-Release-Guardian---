# AI Release Guardian 2.0 Roadmap

## Goal
Turn the original notebook prototype into a deployable AI-assisted QA application while preserving V1 as evidence of project evolution.

## V2 milestones
1. FastAPI backend and health endpoint
2. Extract DOM analysis from the notebook into typed services
3. Playwright-based browser scanner
4. Persistent projects, scans and artifacts
5. Baseline/current release comparison
6. Deterministic risk engine + explainable score
7. Provider-independent LLM layer
8. RAG for QA knowledge and contextual recommendations
9. React/Next.js dashboard
10. Evaluation suite with known UI mutations
11. Docker Compose and CI
12. Public deployment and demo scenario

## Design principle
Code extracts facts; LLM performs reasoning.

The deterministic layer owns DOM facts, diffs and measurable signals. The LLM explains, prioritizes and proposes tests from those facts rather than inventing them.

## V1 -> V2
V1 remains available as the original course prototype. V2 will progressively move notebook logic into tested modules and expose it through API and UI.
