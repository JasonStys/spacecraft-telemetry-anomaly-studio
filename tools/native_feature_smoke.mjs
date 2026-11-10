/** Jason Stys — extracted telemetry analyst workflow and independent boundary/export oracles.
 * Functions: actual run journey; variables: frozen API, episode, annotation and downloaded review.
 * Exact locations: docs/CODE_INDEX.md. No source detector imports or mocked application responses.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { expect } from "@playwright/test";
import { runNativeJourney } from "./native_browser.mjs";

await runNativeJourney(async ({ page, request, outputDirectory, version }) => {
  const status = page.getByRole("status", { name: "Analysis status" });
  await expect(status).toContainText("Complete");
  const response = await request.get("api/run?scenario=isolated-spike");
  assert.equal(response.status(), 200);
  const run = await response.json();
  assert.equal(run.provenance.version, version);
  assert.equal(run.metrics.tp, 1);
  assert.equal(run.episodes.length, 1);
  assert.deepEqual(
    [
      run.episodes[0].start_tick,
      run.episodes[0].end_tick,
      run.episodes[0].end_boundary,
      run.episodes[0].right_censored,
    ],
    [120, 120, "recovery", false],
  );
  await expect(page.locator("#episodes")).toContainText("120–120");
  await page.locator("#episodes select").selectOption("uncertain");
  const note = "Synthetic spike needs human review; <b>plain text</b>.";
  await page.locator("#episodes textarea").fill(note);
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download human review JSON" }).click();
  const download = await pending;
  const output = path.join(outputDirectory, "native-human-review.json");
  await download.saveAs(output);
  const review = JSON.parse(await readFile(output, "utf8"));
  assert.equal(review.run_sha256, run.id);
  assert.deepEqual(review.episodes[0].annotation, { status: "uncertain", note });
  assert.equal(review.episodes[0].end_boundary, "recovery");
  await page.getByRole("combobox", { name: "Scenario", exact: true }).selectOption("nominal");
  await page.getByRole("button", { name: "Analyze telemetry" }).click();
  await expect(status).toContainText("nominal");
  await expect(page.locator("#episodes li")).toHaveCount(0);
  await page
    .getByRole("combobox", { name: "Scenario", exact: true })
    .selectOption("isolated-spike");
  await page.getByRole("button", { name: "Analyze telemetry" }).click();
  await expect(status).toContainText("isolated-spike");
  await expect(page.locator("#episodes textarea")).toHaveValue("");
  assert.equal((await request.get("api/run?threshold=0")).status(), 400);
});
