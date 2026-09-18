# Severity calibration benchmark

This benchmark is a small, manually labelled calibration set for the deterministic risk engine.

Labels represent engineering expectations for controlled mutations, not observed production incidents. The benchmark therefore measures agreement with the current severity rubric, not real-world failure probability.

Endpoint: `GET /api/v1/evaluation/severity`

Reported outputs:
- accuracy;
- per-case expected/predicted level and score;
- LOW/MEDIUM/HIGH/CRITICAL confusion matrix.

The dataset should be expanded and split before using its accuracy as a portfolio performance claim. A future version should contain realistic multi-element flows and independently reviewed severity labels.
