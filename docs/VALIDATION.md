# Validation strategy and observed evidence

By Jason Stys. Local results recorded2026-10-20. The [published CI baseline](reports/CI_BASELINE.md) records actual completed runs; final exact-source checks also gate the portable release.

## Local results

| Gate                                  | Observed result                                                                                                                                                                     |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python                                | 87 tests passed;99.29% branch-aware runtime coverage (required90%)                                                                                                                  |
| Configuration grid                    | All576 finite scenario/duration/fault/seed/multiplier/context combinations exercised                                                                                                |
| Independent detector oracles          | Hand-computed median/MAD; strict limit boundary; EWMA recurrence; exact six-repeat boundary; missing/context resets                                                                 |
| Causality/leakage                     | Future-observation mutation cannot alter earlier rows; label mutation cannot alter model/decisions                                                                                  |
| Parser fuzz/property                  | 100 arbitrary-byte CSV examples and30 detached/deterministic settings examples; bounded, not exhaustive                                                                             |
| TypeScript                            | 11 pure preference/metric/gap-plot tests passed                                                                                                                                     |
| Browser                               | 21/21 tests passed across Chromium/Firefox/WebKit; actual downloads, null metrics, missing gaps, selected tick, retries, storage denial,390px layout and axe WCAG2A/AA/2.1AA checks |
| Ruff / strict mypy / TypeScript build | Passed                                                                                                                                                                              |
| Deterministic benchmark               | 24 scenario/seed metric+hash fixtures in reports/benchmark.json                                                                                                                     |
| Observed runtime                      | 20 uncached480-frame analyses: median13.18ms, max16.76ms on this Windows/Python3.14.6 host; includes alternate strategy/report hash, not a latency guarantee                        |

## Default synthetic benchmark (seed7, multiplier4, context-aware)

| Scenario           | TP  | FP  | FN  | Missing channel-ticks | Delay     |
| ------------------ | --- | --- | --- | --------------------- | --------- |
| nominal            | 0   | 0   | 0   | 0                     | Undefined |
| isolated-spike     | 1   | 0   | 0   | 0                     | 0         |
| multichannel-burst | 24  | 12  | 0   | 0                     | 0         |
| slow-drift         | 23  | 4   | 13  | 0                     | 13        |
| stuck-sensor       | 31  | 4   | 5   | 0                     | 5         |
| telemetry-gap      | 0   | 0   | 0   | 36                    | Undefined |
| partial-dropout    | 0   | 0   | 0   | 12                    | Undefined |
| step-shift         | 36  | 4   | 0   | 0                     | 0         |

These are generated fixtures, not mission accuracy. Other seeds can give materially different precision (including false alarms on the otherwise easy spike case); the committed benchmark includes all three seeds and pooled comparisons. No result is trimmed to make recall look better. Imported unlabeled data has undefined accuracy metrics.

## Requirement traceability

| Requirement                 | Test/evidence                                                                                                                 |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Robust scale and boundaries | test_detector.py independent repeated0..4 center2/MAD1 oracle and exact limit/EWMA/flatline assertions                        |
| Training-only fitting       | Model equality under future/label mutation; complete clean-prefix/characterized-mode validation                               |
| Missing is not zero         | Quality counts, reset tests, exact observed denominators, browser missing-value/segmented-path tests                          |
| Honest evaluation           | TP+FP+FN+TN=observed grid contracts; undefined/unknown metrics; real displayed confusion tables                               |
| CSV boundaries              | Actual numeric round trips; UTF-8/size/NaN/formula/quote/header/clock/row checks and arbitrary-byte corpus                    |
| Local HTTP security         | Actual sockets test Host/Origin/cross-site, paths/symlinks, duplicate/excess/long queries, write methods and header injection |
| Reports/history             | Real CLI and CSV/JSON/HTML exports, immutable/idempotent SQL, hash mismatch and cap refusal                                   |
| UI behavior                 | Production service/assets, three engines, real4-format downloads, selected ledger/tick, defaults and errors/retry             |
| Supply chain/release        | Hash/integrity locks, CodeQL, dependency audits, exact-source draft gate, actual frozen app smoke                             |

## CI and release policy

Validation has8 jobs: Linux Python3.12/3.14, Windows/macOS3.14; one three-engine browser job; three native-platform frozen-app jobs. CodeQL has Python and JavaScript/TypeScript jobs. The24 benchmark hashes are checked across OS/runtime builds. CI enforces headers/docstrings/exact-line/file inventories, formatting, strict types and coverage. No Actions artifacts/caches/database bundles are uploaded; logs remain with each run. Portable releases are separate draft assets with checksum review and downloaded-app validation.

Storage preflight:84 repos,58,024,434 live artifact bytes and14,884,719,852 separate cache bytes. Billing UI showed0.5/0.5GB included Actions storage (100%). Accumulated billing and current live storage differ; no percentage is inferred from current bytes. Nothing was deleted.

## Defects caught before publication

An oversized parser input also generated an oversized test identifier on Windows; descriptive bounded test IDs preserve the exact input test without overflowing the harness environment. A browser locator was corrected to use the actual named combobox role. Firefox exposed genuine mobile intrinsic grid overflow; `minmax(0,1fr)` and an explicit zero minimum on the analysis column fixed it while retaining the DOM-bounds and no-horizontal-overflow regression assertions. No test was skipped, retried blindly or weakened to conceal a failure.

## Limits

Coverage is not correctness proof. Golden reports supplement independent arithmetic/causality oracles, not replace them. Fuzzing is a bounded property corpus, not long-running coverage-guided fuzzing. Automated accessibility scans are not a full human audit. No real spacecraft data, operational validation, root-cause diagnosis, physical accuracy, hard real-time behavior, fault tolerance certification, flight qualification or guarantee of security is established. Linux/macOS executable behavior is tested on their CI runners, not claimed as local Windows execution. Signed/notarized or mobile-native distribution is not supplied.
