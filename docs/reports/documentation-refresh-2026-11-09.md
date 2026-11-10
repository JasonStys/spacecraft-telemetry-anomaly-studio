# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `616b8cc92be09622443e103cdc201ce1d0c16a55`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 |  Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | -----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 105884 | `3cb445410a6035b564385cd49a4e2bebc5bf2897658cabb5f2680d8fdffe9d7e` | 4 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     |  41850 | `6ef9f87f4d56b52801951c2f23c1d2f19ac2404b1192b82487d76bdb5d3545cb` | 3 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |   7404 | `71df134b061db10702612ad0207c2696621a66afd694308f3ad80423a2902908` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `616b8cc92be09622443e103cdc201ce1d0c16a55`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Integration-local checks

Observed at `2026-11-10T07:31:07.918547+00:00` on Windows in this repository’s isolated locked development environment. Commands below use its activated Python environment. The documentation source baseline remains the immutable revision above; these checks validate this documentation integration locally.

| Command                                                           | Observed result |
| ----------------------------------------------------------------- | --------------- |
| `python tools/verify_repo.py --write`                             | Passed, exit 0. |
| `python tools/verify_repo.py`                                     | Passed, exit 0. |
| `python -m ruff check telemetry tests tools launcher.py`          | Passed, exit 0. |
| `python -m ruff format --check telemetry tests tools launcher.py` | Passed, exit 0. |
| `python -m mypy telemetry`                                        | Passed, exit 0. |
| `python -m pytest --cov=telemetry --cov-report=term-missing`      | Passed, exit 0. |
| `node node_modules/prettier/bin/prettier.cjs --check .`           | Passed, exit 0. |
| `node node_modules/vitest/vitest.mjs run`                         | Passed, exit 0. |

The independent publication audit also matched every copied Office file to its approved SHA-256, checked ZIP package integrity and current page/tab approvals, compared immutable workflow/source metadata, and resolved every local handbook/report link within the repository. Hosted PR/main, browser, platform and container jobs remain separate required checks; they are not inferred from these local results.

The unchanged full Python suite passed 179 tests at 99.38% combined statement/branch coverage, retaining the 90% floor; all 13 TypeScript unit tests also passed. Catalog support recognizes only the three named public Office files; it still refuses source-inventory traversal and does not skip unknown binary files.
