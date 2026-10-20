/* Pure plotting, optional preferences and honest display transforms by Jason Stys.
 * Functions: metric, segments, preferences. Variables: bounds, values, finite choices and path parts.
 * Exact lines: docs/CODE_INDEX.md. No interpolation across a missing observation.
 */
import type { Catalog, Settings } from "./types";

/** A metric with zero denominator is undefined, not a perfect or zero detection rate. */
export function metric(value: number | null | undefined, percentage = false): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "Undefined";
  return percentage ? `${(100 * value).toFixed(1)}%` : value.toLocaleString("en-US");
}
/** Create line segments with a new M after every gap; x uses actual integer observation ticks. */
export function segments(
  values: { tick: number; value: number | null }[],
  duration: number,
  low: number,
  high: number,
): string[] {
  const paths: string[] = [];
  let parts: string[] = [];
  for (const { tick, value } of values) {
    if (value === null || !Number.isFinite(value)) {
      if (parts.length) paths.push(parts.join(" "));
      parts = [];
      continue;
    }
    const x = 40 + (tick / Math.max(1, duration - 1)) * 820;
    const y = 220 - ((value - low) / Math.max(1, high - low)) * 175;
    parts.push(`${parts.length ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`);
  }
  if (parts.length) paths.push(parts.join(" "));
  return paths;
}
/** Accept only own allowlisted primitive entries; storage poisoning never becomes executable UI. */
export function preferences(raw: string | null, catalog: Catalog): Settings {
  const result = { ...catalog.defaults };
  if (!raw) return result;
  try {
    const data: unknown = JSON.parse(raw);
    if (!data || typeof data !== "object" || Array.isArray(data)) return result;
    for (const [key, value] of Object.entries(data)) {
      if (
        key === "scenario" &&
        typeof value === "string" &&
        Object.hasOwn(catalog.scenarios, value)
      )
        result.scenario = value;
      else if (
        Object.hasOwn(catalog.choices, key) &&
        typeof value === "number" &&
        catalog.choices[key]?.includes(value)
      )
        Object.assign(result, { [key]: value });
    }
  } catch {
    /* Local preference storage is optional; invalid data is ignored. */
  }
  return result;
}
