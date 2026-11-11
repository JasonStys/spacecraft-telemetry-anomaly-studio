# Spacecraft Telemetry Anomaly Studio handbook

By Jason Stys.

Investigate context-aware anomalies in synthetic spacecraft telemetry while keeping stale, missing and malformed observations explicit. The local workbench combines bounded detection, interactive evidence review and reproducible exports; it does not diagnose or operate real spacecraft.

The released 1.1.0 portable app includes run-bound anomaly triage: inspect channel episodes with explicit recovery, gap, context and censored boundaries, add human notes, and download the review tied to its originating run.

The original label-isolated detector and metrics remain unchanged. An actual extracted-app analyst journey verifies a known spike, annotation export and note reset between analyses; independently restoring the previous version field reproduced every old benchmark hash before version-only IDs were refreshed. This makes the downloadable workflow match the practical source feature without claiming operational anomaly assurance.

## Read the documentation

The [illustrated Windows guide](reports/windows-application-guide.docx) adds actual
installed-app screenshots, a worked scenario, source excerpts and dated acceptance.
Its [review manifest](reports/windows-application-guide.json) identifies the exact
reviewed bytes. Earlier Office editions below retain their historical baselines.

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [RELEASE](RELEASE.md)
- [TRIAGE](TRIAGE.md)
- [USER GUIDE](USER_GUIDE.md)
- [releases/v1.1.0](releases/v1.1.0.md)

### Design and contracts

- [API](API.md)
- [ARCHITECTURE](ARCHITECTURE.md)
- [MODEL](MODEL.md)

### Security and validation

- [SECURITY](SECURITY.md)
- [VALIDATION](VALIDATION.md)

## Historical results and reproduction

The reviewed source is [`616b8cc92be09622443e103cdc201ce1d0c16a55`](https://github.com/JasonStys/spacecraft-telemetry-anomaly-studio/tree/616b8cc92be09622443e103cdc201ce1d0c16a55). The observed functional workflow baseline is `616b8cc92be09622443e103cdc201ce1d0c16a55`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/PORTABLE_REFRESH_20261109.md)
- [Current Actions](https://github.com/JasonStys/spacecraft-telemetry-anomaly-studio/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Synthetic telemetry and bounded rule-based detector evidence; no live spacecraft or hardware validation.
- Human notes are detached local downloads rather than server-persisted multi-user reviews.
- Unsigned desktop portable folders, not system installers or clean-machine proof. Three-OS extracted-native checks drive an owned URL; default OS browser opening remains manual.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
