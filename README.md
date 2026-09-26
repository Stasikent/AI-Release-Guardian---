# AI Release Guardian V2

AI Release Guardian is a QA release-analysis platform that captures real web interfaces, compares releases, prioritizes regression risk, generates deterministic regression tests, and exposes a configurable quality gate for CI/CD.

The core principle is simple:

**Code extracts facts → deterministic QA logic evaluates changes → AI adds grounded reasoning.**

The release decision does not depend on an LLM. DOM diff, risk scoring, regression focus, generated test cases, route readiness, and the release gate all work deterministically.

## What V2 does

- captures pages with Playwright and extracts normalized testable DOM objects;
- stores projects, scans, baseline/current/history state in PostgreSQL;
- compares baseline vs current per route;
- preserves path + query as route identity while ignoring URL fragments;
- calculates field-aware deterministic release risk;
- explains risk contribution down to changed DOM fields;
- builds prioritized regression focus and executable-style test cases without an LLM;
- exports regression tests as JSON, Markdown, and Playwright TypeScript;
- discovers same-origin routes from a site;
- runs resilient multi-route baseline/current batch scans;
- summarizes release readiness across all routes;
- applies a configurable release policy;
- exposes a machine-readable release gate that can block deployment;
- optionally adds grounded AI analysis as a separate layer.

## Architecture

```mermaid
flowchart LR
    URL[Base URL] --> DISC[Route discovery]
    DISC --> BATCH[Multi-route scans]
    BATCH --> DB[(PostgreSQL)]
    DB --> DIFF[Deterministic DOM diff]
    DIFF --> RISK[Field-aware risk engine]
    RISK --> REG[Regression focus + tests]
    REG --> OVERVIEW[Project release overview]
    OVERVIEW --> POLICY[Configurable release policy]
    POLICY --> GATE[Release gate]
    GATE --> CI[GitHub Actions / CI-CD]
    DIFF --> AI[Optional grounded AI analysis]
```

### Backend

FastAPI provides project, scan, comparison, export, route-discovery, batch-scan, release-overview, policy, and release-gate APIs. SQLAlchemy + Alembic manage persistence and migrations. Playwright performs browser capture behind public-URL/SSRF safeguards.

### Frontend

Next.js + TypeScript provides the project workflow, route discovery, selectable batch scans, release overview, risk inspection, policy controls, regression output, and exports.

### QA engine

The deterministic layer owns release-critical behavior. Changed fields receive explicit weights, affected elements are ranked by risk contribution, and regression cases are generated from observable DOM facts. AI analysis is supplemental rather than authoritative.

## End-to-end demo

A reviewer can understand the project with this workflow:

1. Create a project and provide a public target/base URL.
2. Use **Discover routes** to collect unique same-origin pages.
3. Select relevant routes and run **Batch baseline**.
4. Change or deploy a newer version of the target application.
5. Run **Batch current** against the same routes.
6. Open **Project Release Overview**. Each route is reported as `READY`, `MISSING_BASELINE`, or `MISSING_CURRENT`.
7. Inspect deterministic DOM changes, field-level risk contributions, regression focus, and generated regression tests.
8. Configure the policy: block on `HIGH` or `CRITICAL`, set the maximum risk score, and decide whether every discovered route must be complete.
9. Evaluate the project release gate.
10. Allow CI/CD to continue only when Guardian returns `allowed=true`.

A failed page does not abort an entire batch. Guardian records the route failure and continues scanning the remaining selected routes. Batch routes are constrained to the configured origin.

## Example release decision

```
/login              LOW       8/100   READY
/products?page=2    MEDIUM    31/100   READY
/checkout           HIGH      62/100   READY

Policy:
  block_on = HIGH
  max_risk_score = 70
  require_all_routes = true

Release gate:
  BLOCKED
  Reason: at least one route meets the configured HIGH threshold.
```

The important distinction is that the gate is derived from deterministic scan/diff data. An unavailable or differently behaving LLM does not change the deterministic gate result.

## CI/CD release gate

`GET /api/v1/projects/{project_id}/release-gate`

Example:

```json
{
  "project_id": 1,
  "status": "READY",
  "allowed": true,
  "exit_code": 0,
  "reason": "Comparable routes satisfy the configured deterministic release policy.",
  "overall_risk_score": 18,
  "overall_risk_level": "LOW",
  "comparable_routes": 3,
  "incomplete_routes": 0
}
```

`READY` maps to `allowed=true` and `exit_code=0`. `BLOCKED` and `INCOMPLETE` map to `allowed=false` and `exit_code=1`. A successfully evaluated gate returns HTTP 200 so CI can distinguish a release-policy failure from an API/transport failure.

A ready-to-run GitHub Actions example is included in `.github/workflows/release-gate-example.yml`. A deployment job can depend on that gate job with `needs: release-gate`.

## Generated regression artifacts

For a comparable route Guardian can produce:

- deterministic regression priorities;
- structured regression test cases;
- JSON export;
- Markdown export;
- Playwright `.spec.ts` export with field-aware assertions.

A project-wide multi-route Playwright suite can also be exported for the comparable routes.

## Safety and failure behavior

- browser navigation is checked by public-URL validation;
- browser requests are guarded against unsafe targets;
- route discovery keeps only same-origin HTTP/HTTPS links;
- batch scans accept relative routes and verify the resolved target remains on the configured origin;
- failed scans do not archive a valid baseline/current before browser capture succeeds;
- batch failures are isolated per route;
- database mutations use rollback on failure.

## Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic, Playwright  
**Frontend:** Next.js, React, TypeScript  
**Testing/CI:** pytest, integration tests, Docker Compose, GitHub Actions  
**AI layer:** optional LLM analysis grounded in deterministic project data

## Why this project is useful for QA

AI Release Guardian V2 combines several tasks that are often separate in a QA workflow: interface inventory, release comparison, regression prioritization, test generation, multi-page readiness, and CI quality gates. It also makes the boundary between deterministic automation and AI reasoning explicit.

The project is a portfolio/demo system, not a substitute for product-specific QA judgment. Generated checks should be reviewed and supplemented with business-flow, visual, backend, accessibility, performance, and security testing where relevant.
