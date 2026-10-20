# Local API, CSV and evidence

By Jason Stys. Read-only same-origin service, Host exactly `127.0.0.1:<port>`. No CORS, accounts or upload endpoints.

| GET route                      | Response                                                      |
| ------------------------------ | ------------------------------------------------------------- |
| `/api/health`                  | Local educational service status                              |
| `/api/catalog`                 | Finite settings, descriptions, channels and training boundary |
| `/api/run`                     | Schema1 complete synthetic analysis JSON                      |
| `/api/report?format=json`      | Attachment; also `csv`, `html`, `input`                       |
| `/` and `/assets/<built-name>` | Reviewed production HTML/JS/CSS/SVG/ICO only                  |

Run/report parameters: `scenario`, `duration`, `fault_tick`, `seed`, `threshold`, `contextual`; report-only `format`. Public choices are in USER_GUIDE. Defaults are identical in catalog/UI/CLI. Queries are capped at8 fields/1024 characters; duplicates, unknown keys, unsupported values and noninteger settings fail. Text integer spellings accepted by Python (e.g. `0240`) canonicalize to the same numeric value, not different model settings.

Status400 invalid experiment/format/query;403 Host/Origin/cross-site refusal;404 missing or forbidden path;405 writes/HEAD;414 long path;500 unavailable local resource. Errors never echo request text or local source paths. Downloads use fixed names, never request-derived headers. Hidden/source files, encoded/backslash traversal and symlink escapes cannot be served.

## CSV import and output

Only the local CLI accepts an input path. It reads at most cap+1 bytes and refuses files over256,000 bytes. UTF-8 (optional BOM), header exactly `tick,mode,thermal,bus,load`. Exactly240 or480 ordered consecutive frame rows starting at0; mode is SUNLIT/ECLIPSE, channel values are finite within ±10,000 or blank. Wrong row/column counts, bad quotes/encoding, NaN/Infinity, formulas, duplicates/gaps/out-of-order clocks and unknown contexts are rejected. Training additionally requires complete channels and at least12 frames of each context. No path appears in the report. No code, pickles, archives, arbitrary object deserialization or model files are loaded.

`format=input` exports this strict input schema for exact observation round trips. `format=csv` exports a separate evidence schema: run_sha256,tick,mode,channel,value,center,lower,upper,score,drift,repeats,reasons,injected_label. Missing values/scores remain blank, not0. Reasons and text labels come from fixed internal vocabularies. Imported injected_label is `unknown`; synthetic labels are booleans. No arbitrary uploaded strings become formula cells.

## JSON schema1

`id` is SHA256 of sorted compact finite JSON excluding id itself. `observations` retains complete tick/mode/value frames. `rows` contains held-out channel decisions only (tick80 onward), with fitted center/point limits, signed score, causal drift, equal-reading count and fixed reasons. `model` contains frozen band center/scale per channel and context or POOLED. `truth` is a separate tick→channel-name map for synthetic data, null for imports.

`metrics`/`comparison` contain observed/missing/alert counts, TP/FP/FN/TN, precision/recall/F1/delay. Unknown or undefined values are null, not a fabricated estimate. Comparison uses the alternate strategy on identical data; full alternate channel rows are not duplicated in the report. `settings` includes finite generator parameters for synthetic runs, only effective duration/threshold/contextual for imports. `provenance` records author/version/algorithm/source, logical clock, prefix/evaluation bounds, invented units and scope. There are no timestamps or platform-specific paths to break reproducibility.

HTML is escaped JSON in an inert CSP-restricted document with no active scripts. JSON/report SHA values detect differing content but do not authenticate a publisher or establish correctness. See MODEL for exact causal ordering and metric semantics.
