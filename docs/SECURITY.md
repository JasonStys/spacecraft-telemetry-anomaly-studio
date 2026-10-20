# Security and privacy

By Jason Stys. Local teaching analysis, not a public or operational monitoring service.

## Scope and controls

Untrusted numeric input, malformed CSV/query parameters, hostile browser origins, accidental evidence modification and supply-chain errors are in scope. Controls: finite setting allowlists and strict primitive types, bounded records/bytes/grid, finite numeric checks, exact known modes, safe CSV parsing without execution, same-origin/Host enforcement, CSP, no shell, no uploads/remote fetches and confined production assets. Reports use fixed filenames, escaped HTML and typed/fixed-label CSV fields. User content never becomes active HTML or executable model code.

Only IPv4 loopback is bound. Duplicate/wrong Host, foreign Origin and Sec-Fetch-Site cross-site requests are rejected. The service exposes no history path, filesystem browser, mutation, account, device or external API endpoint. Headers deny framing, MIME sniffing, referrer disclosure and unnecessary camera/microphone/location permissions. No remote fonts, tracking, analytics, ad scripts, popups, auto-updater or background system service exists. External repository links require an explicit user click and use noreferrer.

Optional browser storage contains only finite settings. CLI CSV/history paths are explicit local user choices. Imported path names are omitted from evidence. SQLite inserts use placeholders, content hashes detect modification, immutable triggers prevent accidental update/delete, and the100-record cap refuses new data without deletion. OS access controls still matter: local files are not encrypted and privileged users can alter them. Do not commit private operational telemetry; ignored patterns exclude histories, credentials and build/runtime data.

## Limits

Loopback is not protection from local malware or another same-user process. The Python standard-library HTTP server is not hardened for hostile multiuser or Internet hosting. Finite workload limits do not make it a comprehensive denial-of-service defense. Models are not a root-cause diagnosis, calibrated risk score, intrusion detector, safety/flight monitor or guarantee that unflagged data is healthy. Arbitrarily contaminated training is not detected automatically. No spacecraft/device command path exists.

Builds use hash-locked Python and integrity-locked npm dependencies; actions are SHA-pinned, checkout credentials are not persisted, and release publication is separated from PR validation. CodeQL/audits are time-specific checks, not a promise of future vulnerability absence. Desktop builds are unsigned; SHA manifests detect mismatched bytes but are not independent signatures. Never bypass OS trust warnings or disable protections.

## Reporting and recovery

Use GitHub private vulnerability reporting if available; otherwise contact [Jason Stys](https://github.com/JasonStys) to arrange a private channel. Do not publish credentials, private telemetry, personal data or sensitive exploit details in issues. Stop a suspect local build, preserve synthetic reproduction evidence, and rebuild an earlier reviewed source or wait for a repaired release. Do not delete or mutate user histories as part of rollback. No public hosting or account-setting change is authorized by these workflows.
