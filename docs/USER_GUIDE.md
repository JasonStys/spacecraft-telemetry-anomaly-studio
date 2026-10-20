# User guide

By Jason Stys. All supplied scenarios and the example CSV are synthetic.

## First analysis

Launch the extracted desktop app or run `python -m telemetry serve` after the source build. Use its printed `127.0.0.1` URL. The default isolated spike appears at tick120 on the thermal channel. Its point residual exceeds the frozen SUNLIT band, and the ledger identifies the rule. The shaded prefix0–79 is training-only; evaluation begins at80.

Choose slow drift and Analyze telemetry. At default seed7/multiplier4, the first true positive is13 ticks into the injected interval; some biased readings are missed, and residual temporal memory adds false positives after recovery. Compare the selected strategy with the alternate pooled/context-aware model. Try seed101 to see why one carefully chosen perfect example is not general accuracy evidence.

Choose partial dropout, select the bus channel and inspect tick125. Value is Missing, residual/drift are unavailable, the line is split and the decision is QUALITY GAP. Switch to thermal: it remains observable. Full telemetry gap has36 missing channel-ticks (12 frames ×3 channels), not36 failed sensor detections.

## Controls and meaning

| Setting          | Allowed choices                                             |
| ---------------- | ----------------------------------------------------------- |
| Scenario         | Eight reviewed fixtures                                     |
| Duration         | 240 or480 logical frames                                    |
| Inject at        | 120 or160, always after training                            |
| Seed             | 7 /23 /101                                                  |
| Limit multiplier | 3 /4 /6 robust scale multiples, not a confidence percentage |
| Baseline         | Context-aware (separate mode bands) or pooled               |

Selections are pending until Analyze telemetry. Downloads remain tied to the last completed run, never silently relabeled by a pending selection. Restore defaults starts a new default analysis. New runs/errors hide previous evidence; Retry retries the current finite selection. The channel/tick controls inspect the completed run without retraining. The label overlay is evaluation truth only, never detector input. Ledger buttons inspect their exact tick; its filter can show alerts, gaps or both for the selected channel.

Only finite settings are optionally saved in browser local storage. Storage denial, malformed JSON or inherited/prototype keys cannot prevent normal analysis. No remote service, account, telemetry collection, background task or device connection is installed.

## Reports and local CSV

JSON retains all observations, decisions, bands, settings, labels (synthetic only), metrics, alternate-strategy metrics and provenance. Evidence CSV has one row per evaluation channel-tick, with blank missing values and explicit labels. HTML is escaped structured evidence with no scripts. Input CSV has the strict import schema; it intentionally has no labels.

```powershell
python -m telemetry export --scenario slow-drift --format input --output input.csv
python -m telemetry export --input input.csv --format html --output analysis.html
python -m telemetry export --scenario slow-drift --output evidence.json --history local-runs.sqlite3
```

Use your venv Python path if needed. Exports refuse to overwrite. History is opt-in, idempotent for matching evidence, immutable through its SQL schema and capped at100 unique reports. At the cap choose a new database; the app never deletes old records. Export and history are separate destinations, not an atomic cross-file transaction.

CSV imports require exactly `tick,mode,thermal,bus,load`, UTF-8 (optional BOM), 240 or480 ordered consecutive ticks starting at0, mode SUNLIT/ECLIPSE, bounded finite numeric values or blank absence. Training must have complete observations and both characterized modes. The cap is256,000 bytes; archives, formulas, other columns and automatic sorting/truncation are refused. Imported accuracy stays undefined because the app cannot infer true faults from unlabeled data. Fault/seed settings are not applied to imports. Read [API](API.md) for details.

## Troubleshooting and support

- Source build missing: `npm ci` then `npm run build`.
- Unsupported Python: use3.12–3.14 and the hash-locked development requirements.
- Port busy: use an ephemeral default, or a free `--port`; only IPv4 loopback is supported.
- Export exists: choose a new filename. No automatic overwrite/deletion.
- Bad training/CSV: review the explicit error and schema; do not invent missing training measurements.
- Unsigned app blocked: do not disable protections or bypass security warnings; review/build source or wait for a trusted signed distribution.

Ctrl+C stops the local console service. Keep the extracted bundle intact. Mobile responsiveness is provided, not a phone-native app or publicly hosted website. Contact [Jason Stys](https://github.com/JasonStys) or open an issue using synthetic settings and report ID. Keep private telemetry, paths and credentials out of public issues.
