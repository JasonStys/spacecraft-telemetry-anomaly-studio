/* Actual production browser tests by Jason Stys. Functions: ready, choose, inspect and test cases.
 * Variables: detector fixtures, real downloads, mobile layout and optional-storage failures.
 * Exact declaration/variable locations: docs/CODE_INDEX.md. Tests exercise the real local service.
 */
import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";

/** Wait for the named analysis status, not an unrelated implicit live region. */
async function ready(page: Page): Promise<void> {
  await page.goto("/");
  await expect(page.getByRole("status", { name: "Analysis status" })).toContainText("Complete");
}
/** Run a finite fault through the actual form and detector service. */
async function choose(page: Page, scenario: string): Promise<void> {
  await page.getByRole("combobox", { name: "Scenario", exact: true }).selectOption(scenario);
  await page.getByRole("button", { name: "Analyze telemetry" }).click();
  await expect(page.getByRole("status", { name: "Analysis status" })).toContainText(scenario);
}
/** Set the native range's value and dispatch the same input event as pointer/keyboard interaction. */
async function inspect(page: Page, tick: number): Promise<void> {
  await page.locator("#tick").evaluate((node: HTMLInputElement, value) => {
    node.value = String(value);
    node.dispatchEvent(new Event("input", { bubbles: true }));
  }, tick);
}

test("native analysis and explainable selected spike", async ({ page }) => {
  await ready(page);
  await expect(page.locator("#precision")).toHaveText("100.0%");
  await expect(page.locator("#recall")).toHaveText("100.0%");
  await expect(page.locator("#decision")).toHaveText("FLAGGED");
  await expect(page.locator("#explanation")).toContainText("point-limit");
  await inspect(page, 119);
  await expect(page.locator("#decision")).toHaveText("Within rules");
  await page.getByLabel("Show injected labels").check();
  await expect(page.locator(".truth-label")).toHaveCount(1);
});
test("missing values are gaps, partial loss does not hide other channels", async ({ page }) => {
  await ready(page);
  await choose(page, "partial-dropout");
  await page.getByRole("combobox", { name: "Inspect channel" }).selectOption("1");
  await inspect(page, 125);
  await expect(page.locator("#value")).toHaveText("Missing");
  await expect(page.locator("#decision")).toHaveText("QUALITY GAP");
  await expect(page.locator("path.observations")).toHaveCount(2);
  await expect(page.locator("#missing")).toHaveText("12");
  await page.getByRole("combobox", { name: "Inspect channel" }).selectOption("0");
  await expect(page.locator("#value")).not.toHaveText("Missing");
  await expect(page.locator("path.observations")).toHaveCount(1);
});
test("undefined precision and confusion counts are honest", async ({ page }) => {
  await ready(page);
  await choose(page, "nominal");
  await expect(page.locator("#precision")).toHaveText("Undefined");
  await expect(page.locator("#recall")).toHaveText("Undefined");
  await expect(page.locator("#comparison tr").first()).toContainText("480");
  await expect(page.locator("#events")).toContainText("No matching");
  await choose(page, "slow-drift");
  await expect(page.locator("#delay")).toHaveText("13 ticks");
  await expect(page.locator("#precision")).not.toHaveText("100.0%");
  await page.getByRole("button", { name: "Restore defaults" }).click();
  await expect(page.getByRole("status", { name: "Analysis status" })).toContainText(
    "isolated-spike",
  );
});
test("all four real exports preserve detector and quality evidence", async ({ page }) => {
  await ready(page);
  for (const format of ["json", "csv", "html", "input"]) {
    const pending = page.waitForEvent("download");
    await page.locator(`#download-${format}`).click();
    const download = await pending;
    const path = await download.path();
    expect(path).not.toBeNull();
    const body = await readFile(path!, "utf8");
    if (format === "json") {
      expect(JSON.parse(body).metrics.tp).toBe(1);
      expect(JSON.parse(body).provenance.training_ticks).toEqual([0, 79]);
    }
    if (format === "csv") {
      expect(body).toContain("injected_label");
      expect(body.split("\n")).toHaveLength(482);
    }
    if (format === "input") {
      expect(body).toMatch(/^tick,mode,thermal,bus,load/);
      expect(body.split("\n")).toHaveLength(242);
    }
    if (format === "html") {
      expect(body).toContain("Content-Security-Policy");
      expect(body).not.toContain("<script");
    }
  }
});
test("failed analysis hides stale results and retry recovers", async ({ page }) => {
  await ready(page);
  await page.route("**/api/run?**", (route) => route.fulfill({ status: 503, body: "unavailable" }));
  await page.getByRole("button", { name: "Analyze telemetry" }).click();
  await expect(page.getByRole("status", { name: "Analysis status" })).toContainText(
    "Analysis failed",
  );
  await expect(page.locator("#results")).toBeHidden();
  await page.unroute("**/api/run?**");
  await page.getByRole("button", { name: "Retry analysis" }).click();
  await expect(page.getByRole("status", { name: "Analysis status" })).toContainText("Complete");
});
test("mobile accessibility and denied local storage", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      get() {
        throw new DOMException("blocked", "SecurityError");
      },
    });
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze())
      .violations,
  ).toEqual([]);
  const overflow = await page.evaluate(() =>
    [...document.querySelectorAll("body *")]
      .filter((node) => node.getBoundingClientRect().right > window.innerWidth + 1)
      .slice(0, 12)
      .map((node) => ({
        tag: node.tagName,
        id: node.id,
        class: node.className,
        right: node.getBoundingClientRect().right,
      })),
  );
  expect(overflow).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await choose(page, "telemetry-gap");
  await expect(page.locator("#missing")).toHaveText("36");
});
test("finite preferences, ledger filters and constrained API", async ({ page, request }) => {
  await ready(page);
  await choose(page, "stuck-sensor");
  await page.reload();
  await expect(page.getByRole("status", { name: "Analysis status" })).toContainText("stuck-sensor");
  await page.getByRole("combobox", { name: "Show entries" }).selectOption("alerts");
  await page.getByRole("button", { name: "Inspect thermal at tick 125", exact: true }).click();
  await expect(page.locator("#explanation")).toContainText("flatline");
  expect((await request.get("/api/run?threshold=0")).status()).toBe(400);
  expect(
    (await request.get("/api/run", { headers: { Origin: "https://evil.example" } })).status(),
  ).toBe(403);
});
