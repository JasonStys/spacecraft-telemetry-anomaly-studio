# First published CI evidence

Observed2026-10-20 by Jason Stys. Source `b55af190eb8ab7117352ff605743c7b4aedf16fa`.

- [Validation run39507998935](https://github.com/JasonStys/spacecraft-telemetry-anomaly-studio/actions/runs/39507998935): **8/8 jobs passed**. The87-test Python suite, branch-aware coverage gate,576-case configuration grid, lint/types/index checks and24 deterministic benchmark fixtures passed across Linux/Python3.12/3.14, Windows3.14 and macOS3.14.
- [Browser job](https://github.com/JasonStys/spacecraft-telemetry-anomaly-studio/actions/runs/39507998935/job/118921685563): **21/21 passed** across Chromium/Firefox/WebKit;11 TypeScript pure tests and npm audit passed. Production-service tests read actual4-format download bodies, gaps, undefined metrics, retry behavior, preferences, mobile bounds and accessibility scans.
- All three native-platform frozen-app jobs passed: the actual packaged executable exported evidence, served built assets and answered real health/scenario requests. Only its owned child process was stopped by the smoke tool.
- [CodeQL run39507998849](https://github.com/JasonStys/spacecraft-telemetry-anomaly-studio/actions/runs/39507998849): **2/2 language jobs passed**. One informational `py/empty-except` note identified an insufficiently explained expected ValueError branch in a parser-fuzz test. The test now uses an explicit documented return for that expected rejection; unexpected exceptions still fail. The final revision is reanalyzed rather than manually dismissing the note.
- Python/npm dependency audits passed. No Actions artifacts or caches were uploaded by this repository; no account data elsewhere was deleted.

This is a real baseline, not a fabricated future run or certification. Final exact-source Validation and CodeQL success are separately required by release preparation, and final workflow/source/download verification is recorded in release notes. The synthetic benchmark demonstrates this code's defined behavior, not flight accuracy, causal diagnosis, real-time assurance or absence of vulnerabilities.
