# Build, release and rollback

By Jason Stys. Unsigned offline desktop bundles; no installer elevation or real spacecraft integration.

## Preflight

Review source and limitations, install locked development dependencies, build the TypeScript assets and run lint/types/Python tests/browser tests/benchmark/index checks. Check account Actions storage before CI; do not delete runs/artifacts/caches without fresh user approval. All8 Validation jobs and both CodeQL language jobs must pass at the exact release-source SHA. Runtime coverage is branch-aware and gated at90%; no security/mission certification is implied.

Run `python tools/package_app.py` on the target OS. PyInstaller bundles the production assets, local Python application, SQL resources and project/CPython/PyInstaller notices. The script actually executes the frozen program before creating the ZIP: export evidence, start loopback HTTP, exercise health/scenario endpoints, inspect real built web assets, then stop its owned process. `python tools/smoke_app.py <executable>` repeats this smoke.

## GitHub workflow

Dispatch Portable release on main with a new digits.digits.digits version. `prepare_release.py` validates the version and requires successful Validation/CodeQL workflow runs at GITHUB_SHA before creating a new draft. Windows/Linux/macOS jobs independently build, freeze, smoke and produce one ZIP/SHA256 pair. `upload_release.py` refuses public releases or unexpected asset sets; it uploads directly to that draft, not Actions artifact storage. No existing release is overwritten or published automatically.

Before publishing, confirm all jobs succeeded, six expected uploaded assets exist, all downloaded ZIP checksums match, and the newly downloaded matching local OS app actually works. Record exact-source workflow links and verification in release notes. Publish the draft only after this review. Do not reuse a version or replace published binaries to conceal changes.

## Run and stop

Extract the complete OS/architecture-matching bundle. Launch TelemetryAnomalyStudio (`.exe` on Windows) to open its local website. `serve --no-browser` prints its loopback URL instead. Ctrl+C stops the console. Nothing installs an OS service or scheduled task. Keep the resource folder intact; moving only the executable breaks data discovery. Windows/Linux/macOS runners test their own native bundles; this is not universal OS/ABI compatibility. Mobile layout is tested, not native mobile packaging.

## Rollback triggers and procedure

Stop using a release if hashes mismatch, schema/causal contracts regress, the app crashes, private data appears in evidence or a trust issue is suspected. Preserve synthetic evidence, identify the affected source/release and use a reviewed earlier build or rebuild source. Mark the affected release unsuitable rather than silently replacing assets. Choose a new export/history destination for schema changes; never delete or mutate saved histories to make a migration pass. Public hosting, real device remediation and remote production rollback are outside this project's scope.
