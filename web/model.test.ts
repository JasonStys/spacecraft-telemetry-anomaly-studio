/* Pure browser contracts by Jason Stys. Variables: gaps, finite catalog and poisoned preferences.
 * Functions: Vitest cases. Exact source/declaration locations: docs/CODE_INDEX.md.
 */
import { expect, it } from "vitest";
import { metric, preferences, segments } from "./model";
import type { Catalog } from "./types";
const catalog: Catalog = {
  scenarios: { nominal: "healthy" },
  choices: { duration: [240, 480] },
  defaults: {
    scenario: "nominal",
    duration: 240,
    fault_tick: 120,
    threshold: 4,
    seed: 7,
    contextual: 1,
  },
  channels: ["thermal", "bus", "load"],
  training: 80,
};
for (const raw of [
  null,
  "{",
  "null",
  "[]",
  "false",
  '"text"',
  '{"scenario":"toString","constructor":2,"__proto__":{"x":1}}',
])
  it(`rejects invalid preferences ${raw}`, () =>
    expect(preferences(raw, catalog)).toEqual(catalog.defaults));
it("accepts only finite own choices", () =>
  expect(preferences('{"duration":480,"seed":true,"scenario":"bad"}', catalog)).toEqual({
    ...catalog.defaults,
    duration: 480,
  }));
it("does not turn missing or undefined precision into a perfect score", () => {
  expect(metric(null, true)).toBe("Undefined");
  expect(metric(undefined)).toBe("Undefined");
  expect(metric(NaN)).toBe("Undefined");
  expect(metric(0, true)).toBe("0.0%");
  expect(metric(1, true)).toBe("100.0%");
});
it("gaps break lines, genuine zero remains present", () => {
  expect(
    segments(
      [
        { tick: 0, value: 0 },
        { tick: 1, value: null },
        { tick: 2, value: 2 },
      ],
      3,
      0,
      2,
    ),
  ).toHaveLength(2);
  expect(
    segments(
      [
        { tick: 0, value: 0 },
        { tick: 1, value: 1 },
      ],
      2,
      0,
      2,
    )[0],
  ).toContain("L");
});
it("empty/missing/nonfinite and flat ranges remain finite", () => {
  expect(segments([], 0, 1, 1)).toEqual([]);
  expect(
    segments(
      [
        { tick: 0, value: null },
        { tick: 1, value: NaN },
      ],
      2,
      0,
      1,
    ),
  ).toEqual([]);
  expect(segments([{ tick: 0, value: 1 }], 1, 1, 1)[0]).not.toContain("NaN");
});
