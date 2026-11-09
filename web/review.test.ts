/* Run-bound review contract tests by Jason Stys. Variables: detached fixture and invalid notes.
 * Functions: Vitest cases. Exact lines: docs/CODE_INDEX.md.
 */
import { expect, it } from "vitest";
import { reviewDocument } from "./review";
import type { Run } from "./types";
const run = { id: "a".repeat(64), episodes: [{ id: "thermal:120:cruise" }] } as Run;
it("exports plain notes bound to the evidence hash and leaves the run unchanged", () => {
  const before = JSON.stringify(run);
  const result = reviewDocument(run, {
    "thermal:120:cruise": { status: "uncertain", note: "<script>inert</script>" },
  });
  expect(result).toMatchObject({ run_sha256: run.id, schema: "telemetry-human-review-v1" });
  expect(JSON.stringify(run)).toBe(before);
});
it("rejects stale episode identifiers, unsupported status and oversized notes", () => {
  for (const annotations of [
    { old: { status: "explained", note: "" } },
    { "thermal:120:cruise": { status: "healthy", note: "" } },
    { "thermal:120:cruise": { status: "explained", note: "x".repeat(1001) } },
  ])
    expect(() => reviewDocument(run, annotations)).toThrow("Invalid run-bound");
  expect(reviewDocument(run, {})).toMatchObject({
    episodes: [{ annotation: { status: "unreviewed", note: "" } }],
  });
});
