# References and distribution notices

By Jason Stys. Original application code is MIT licensed. Local HTTP/report/release/index tooling is adapted from the author's earlier portfolio work; the telemetry generator, detector, evaluation, importer, tests and signal UI are specific to this repo.

## Primary references

- [NIST median absolute deviation](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm) and [measures of scale](https://itl.nist.gov/div898/handbook/eda/section3/eda356.htm) explain robust scale estimation. The conventional factor1.4826 is not a calibrated probability for this invented non-Gaussian stream.
- [NASA cruise operations](https://science.nasa.gov/learn/basics-of-space-flight/chapter15-1/) describes telemetry quality/alarm-limit work and human operational responsibility. This project is not flight operations software and uses no mission data.
- [NASA anomaly-detection software catalog](https://software.nasa.gov/software/NPO-50838-1) is context for the broader field. That LSTM software is **not integrated, reproduced, benchmarked or claimed equivalent** here. This repo deliberately uses small explainable statistical rules.
- [Python csv](https://docs.python.org/3/library/csv.html) and [statistics](https://docs.python.org/3/library/statistics.html) are the runtime library references; code never executes CSV content or loads model objects.

No external dataset, model weight, artwork, spacecraft telemetry, vendor API or proprietary document is bundled. All examples are generated synthetic numeric data; UI graphics are SVG primitives. No NASA/agency endorsement, operational fitness or flight qualification is implied.

## Licenses and runtime

Runtime is Python's standard library plus compiled authored TypeScript/HTML/CSS. CPython's full license is in `licenses/PYTHON.txt`. Each frozen bundle includes the project MIT license, CPython notice and the locked PyInstaller distribution's COPYING notice. PyInstaller's GPL exception permits distribution of generated bundles under compatible application licensing; see [official PyInstaller license](https://pyinstaller.org/en/stable/license.html). Platform runtime/ABI and OS trust restrictions still apply; builds are unsigned.

Exact development versions/hashes are in requirements-dev.lock and package-lock.json. TypeScript and Playwright use Apache-2.0; Vite/Vitest/Prettier use MIT; axe-core uses MPL-2.0. pytest, Hypothesis, ruff, mypy, coverage and audit/build tooling retain their distribution license metadata. They are development tools, not remotely loaded browser scripts. No unused native compiler/coverage tooling is required by this project. Dependency audits describe observed advisories at validation time, not a continuing guarantee.
