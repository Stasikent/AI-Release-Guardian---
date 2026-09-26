# V2 deterministic risk model

The risk score is a transparent heuristic, not a learned probability of regression.

Structural events and changed fields receive different weights. Removing an interactive element is more severe than adding one. State changes such as `disabled`, `required`, or `readonly` are weighted above cosmetic text/class changes. Navigation target changes are also elevated.

Current field weights are intentionally explicit in `backend/app/risk/engine.py` so they can be tested, reviewed and later calibrated against labelled release examples.

Important: the numeric score (0–100) is an engineering prioritization signal. It must not be described as a validated probability or production failure rate.

Calibration roadmap:
1. build labelled realistic mutation cases;
2. compare heuristic severity with expected severity;
3. measure disagreement by field/change category;
4. tune weights on a training split;
5. report performance on a held-out evaluation split.
