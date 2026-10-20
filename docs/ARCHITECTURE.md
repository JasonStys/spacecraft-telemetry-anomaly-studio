# Architecture and decisions

By Jason Stys. Accepted scope: local, inspectable statistical telemetry teaching application.

```text
Finite UI settings → deterministic synthetic observations ─┐
CLI strict numeric CSV → bounded local observations ───────┤
                                                         ↓
          ticks0–79 → frozen median/MAD bands → causal scoring of ticks80+
                                                         ↓
          separate synthetic labels → evaluator only → evidence/plots/reports
CLI opt-in → content-verified immutable SQLite history
```

## ADR1 — Transparent statistics before opaque models

Python implements robust fitting and causal streaming rules with only the standard library. TypeScript owns strict UI contracts and SVG inspection; HTML/CSS provide semantic responsive presentation; SQL provides local transactional history. These languages fit the actual work. A native/extra-language bridge or neural runtime would increase distribution and audit complexity without improving this bounded dataset's inspectability. The project does not claim a neural-network implementation or integrate NASA anomaly-detection software.

NASA's operations material describes evaluating telemetry quality and alarm limits; NIST describes MAD as a robust scale estimate. Those concepts inform the lab, not a claim of mission readiness. [NASA cruise operations](https://science.nasa.gov/learn/basics-of-space-flight/chapter15-1/), [NIST MAD](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm).

## ADR2 — Structural label isolation and frozen training

`Frame` contains only tick/mode/values. `fit` accepts only an explicit training list. `Detector.observe` accepts only one frame. Labels enter `metrics` after rows are generated. Future-value and label-mutation regression tests verify this boundary. Training/evaluation and context categories are assumptions documented for the synthetic fixture; real nonstationarity/contaminated training remains a limitation. No automatic relearning, tuning against truth or favorable interval relabeling is hidden in the UI.

## ADR3 — Separate absence from anomaly

Missing observations reset temporal memory, never become zeros, and do not enter confusion counts. The quality count and per-channel gap visualization remain visible. Source data is retained in evidence; no imputation or silent row deletion occurs. Unknown modes or malformed clocks fail rather than guessing an operational state.

## ADR4 — Local read-only boundary

The server binds only IPv4 loopback, enforces exact Host/same-origin/cross-site constraints, has no mutation/upload/external-fetch/account endpoints and serves only the production assets. CSV import is CLI-only, deliberately outside HTTP. A portable frozen Python application launches the same browser service. No public hosting, installer elevation, phone-native package or real spacecraft connection. Remote multiuser hosting would require a separate security design and user approval.

## ADR5 — Reproducible evidence, not a perfect score

The report contains settings, model bands, complete decisions, quality, truth (when known), alternate strategy and canonical SHA256. The24 seed/scenario benchmark fixtures preserve actual false positives/misses and cross-platform hashes. Independent statistic/decision/causality oracles supplement golden files. Timing is observed, not a flaky CI pass threshold. Local history uses hashes, parameterized SQL and immutable triggers but is not tamper-proof against privileged local filesystem users.

## ADR6 — Storage-conscious publication

The account Actions billing allowance is currently full. Workflows disable automatic Node/CodeQL caching and upload no Actions artifacts/databases. Logs remain on GitHub. Three portable ZIP/checksum pairs upload directly to a new draft release only after exact-source Validation/CodeQL checks pass. No existing account runs/artifacts/caches are deleted. Release assets are separate from Actions storage.

Before expanding: add versioned schemas, context validation, genuinely representative mission data and permission provenance, independent event-level evaluation, calibrated operational thresholds, a broader threat model and expert review. This code must not be connected to real flight systems as-is.
