/* Offline telemetry analysis, chart and evidence UI by Jason Stys.
 * Functions: element, text, selected, chart, inspect, ledger, load, configure, start.
 * Variables: catalog/run, request generation, abort owner, channel/tick and SVG scale bounds.
 * Exact definition/variable lines: docs/CODE_INDEX.md. Evidence is written only as safe DOM text.
 */
import "./style.css";
import { metric, preferences, segments } from "./model";
import type { Catalog, Metrics, Run, Settings } from "./types";

/** Require authored DOM identifiers; do not continue with a missing control or panel. */
function element<T extends HTMLElement>(id: string): T {
  const value = document.getElementById(id);
  if (!value) throw new Error(`Missing element ${id}`);
  return value as T;
}
/** Never turn evidence or error text into executable HTML. */
function text(id: string, value: string): void {
  element(id).textContent = value;
}
let catalog: Catalog;
let run: Run | undefined;
let controller: AbortController | undefined;
let generation = 0;
let tick = 120;
let low = 0;
let high = 1;

/** Read finite form values; the server validates them independently before analysis. */
function selected(): Settings {
  return Object.fromEntries(
    [...new FormData(element<HTMLFormElement>("config")).entries()].map(([key, value]) => [
      key,
      key === "scenario" ? String(value) : Number(value),
    ]),
  ) as unknown as Settings;
}
/** Append one owned SVG primitive using fixed attribute keys and numeric/text values. */
function svgNode(tag: string, attributes: Record<string, string>, label?: string): SVGElement {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  if (label !== undefined) node.textContent = label;
  element("chart").append(node);
  return node;
}
/** Render full observations/limits with honest missing-value segments and optional evaluation truth. */
function chart(): void {
  if (!run) return;
  const index = Number(element<HTMLSelectElement>("channel").value);
  const observations = run.observations.map((frame) => ({
    tick: frame.tick,
    value: frame.values[index] ?? null,
  }));
  const limits = run.rows.map((row) => ({
    tick: row.tick,
    lower: row.channels[index]!.lower,
    upper: row.channels[index]!.upper,
  }));
  const finite = observations.flatMap((row) => (row.value === null ? [] : [row.value]));
  low = Math.min(...finite, ...limits.map((r) => r.lower)) - 6;
  high = Math.max(...finite, ...limits.map((r) => r.upper)) + 6;
  const duration = run.observations.length;
  element("chart").replaceChildren();
  svgNode("rect", {
    x: "40",
    y: "20",
    width: String((79 / (duration - 1)) * 820),
    height: "200",
    fill: "#eee8cf",
  });
  svgNode("text", { x: "47", y: "34" }, "TRAINING");
  for (let part = 0; part <= 4; part++) {
    const value = low + ((high - low) * part) / 4;
    const y = 220 - (part / 4) * 175;
    svgNode("line", { x1: "40", x2: "860", y1: String(y), y2: String(y), stroke: "#dfe5df" });
    svgNode("text", { x: "2", y: String(y + 4) }, value.toFixed(0));
    const x = 40 + (part / 4) * 820;
    svgNode(
      "text",
      { x: String(x - 7), y: "244" },
      String(Math.round((part / 4) * (duration - 1))),
    );
  }
  for (const field of ["lower", "upper"] as const)
    for (const path of segments(
      limits.map((row) => ({ tick: row.tick, value: row[field] })),
      duration,
      low,
      high,
    ))
      svgNode("path", { d: path, class: "limits" });
  for (const path of segments(observations, duration, low, high))
    svgNode("path", { d: path, class: "observations" });
  for (const row of run.rows) {
    const decision = row.channels[index]!;
    if (decision.value !== null && decision.reasons.length)
      svgNode("circle", {
        cx: String(40 + (row.tick / (duration - 1)) * 820),
        cy: String(220 - ((decision.value - low) / (high - low)) * 175),
        r: "3.3",
        fill: "#b83930",
        class: "alert-point",
      });
    if (
      element<HTMLInputElement>("labels").checked &&
      run.truth?.[String(row.tick)]?.includes(decision.channel)
    )
      svgNode("rect", {
        x: String(40 + (row.tick / (duration - 1)) * 820),
        y: "254",
        width: "3",
        height: "5",
        fill: "#ad711f",
        class: "truth-label",
      });
  }
  svgNode("line", {
    id: "cursor",
    x1: "40",
    x2: "40",
    y1: "20",
    y2: "220",
    stroke: "#132d39",
    "stroke-dasharray": "3 4",
  });
  inspect();
  ledger();
}
/** Explain one observed decision; missing and not-scored remain distinct from a nominal reading. */
function inspect(): void {
  if (!run) return;
  const index = Number(element<HTMLSelectElement>("channel").value);
  const row = run.rows[tick - 80];
  if (!row) return;
  const decision = row.channels[index]!;
  text("tick-label", String(tick));
  text("mode", row.mode);
  element<HTMLInputElement>("tick").value = String(tick);
  text("value", decision.value === null ? "Missing" : metric(decision.value));
  text("score", decision.score === null ? "Unavailable" : `${decision.score.toFixed(2)} × scale`);
  text("drift", decision.drift === null ? "Unavailable" : decision.drift.toFixed(2));
  text(
    "decision",
    decision.value === null ? "QUALITY GAP" : decision.reasons.length ? "FLAGGED" : "Within rules",
  );
  const explanation =
    decision.value === null
      ? "No observation: scoring and temporal memory are reset for this channel. This is not evidence that the sensor is healthy."
      : `${decision.channel} / ${row.mode}: center ${decision.center.toFixed(1)}, point limits ${decision.lower.toFixed(2)} to ${decision.upper.toFixed(2)}. ${decision.reasons.length ? `Triggered: ${decision.reasons.join(", ")}.` : "No rule triggered."} Consecutive equal readings: ${decision.repeats}.`;
  text("explanation", explanation);
  const x = 40 + (tick / (run.observations.length - 1)) * 820;
  element("cursor").setAttribute("x1", String(x));
  element("cursor").setAttribute("x2", String(x));
}
/** Show only actual alert/gap channel-ticks, with buttons that inspect the corresponding evidence. */
function ledger(): void {
  const list = element("events");
  list.replaceChildren();
  if (!run) return;
  const index = Number(element<HTMLSelectElement>("channel").value);
  const filter = element<HTMLSelectElement>("ledger-filter").value;
  for (const row of run.rows) {
    const decision = row.channels[index]!;
    const missing = decision.value === null;
    if (
      (!missing && !decision.reasons.length) ||
      (filter === "alerts" && missing) ||
      (filter === "missing" && !missing)
    )
      continue;
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `T+${row.tick}`;
    button.setAttribute("aria-label", `Inspect ${decision.channel} at tick ${row.tick}`);
    button.addEventListener("click", () => {
      tick = row.tick;
      inspect();
    });
    item.append(
      button,
      `${row.mode} / ${missing ? "missing observation" : decision.reasons.join(" + ")}`,
    );
    list.append(item);
  }
  if (!list.childElementCount) {
    const item = document.createElement("li");
    item.className = "empty";
    item.textContent = "No matching flags or missing observations for this channel.";
    list.append(item);
  }
}
/** Display observed confusion counts and undefined denominators without inflated accuracy claims. */
function evaluation(): void {
  if (!run) return;
  for (const key of ["precision", "recall"]) text(key, metric(run.metrics[key], true));
  text("delay", run.metrics.delay === null ? "Undefined" : `${metric(run.metrics.delay)} ticks`);
  text("missing", metric(run.metrics.missing));
  const body = element("comparison");
  body.replaceChildren();
  const strategies: [string, Metrics][] = [
    [run.settings.contextual ? "Context-aware (selected)" : "Pooled (selected)", run.metrics],
    [run.settings.contextual ? "Pooled comparison" : "Context-aware comparison", run.comparison],
  ];
  for (const [name, values] of strategies) {
    const row = document.createElement("tr");
    const header = document.createElement("th");
    header.scope = "row";
    header.textContent = name;
    row.append(header);
    for (const key of ["tp", "fp", "fn", "tn", "f1"]) {
      const cell = document.createElement("td");
      cell.textContent = metric(values[key], key === "f1");
      row.append(cell);
    }
    body.append(row);
  }
  text(
    "provenance",
    `${run.provenance.algorithm}\nTraining: 0–79. Evaluation: 80–${run.observations.length - 1}.\nSource: ${run.provenance.source}\nEvidence SHA-256: ${run.id}`,
  );
}
/** Clear stale evidence during request/error; a superseded response cannot publish a result. */
async function load(): Promise<void> {
  controller?.abort();
  controller = new AbortController();
  const active = ++generation;
  const settings = selected();
  const query = new URLSearchParams(Object.entries(settings).map(([k, v]) => [k, String(v)]));
  run = undefined;
  element("results").hidden = true;
  element("retry").hidden = true;
  element<HTMLButtonElement>("apply").disabled = true;
  text("status", "Fitting the training prefix and scoring held-out observations…");
  try {
    const response = await fetch(`/api/run?${query}`, { signal: controller.signal });
    if (!response.ok) throw new Error("Local analysis unavailable");
    const data = (await response.json()) as Run;
    if (active !== generation) return;
    run = data;
    tick = run.settings.fault_tick;
    element<HTMLInputElement>("tick").max = String(run.observations.length - 1);
    try {
      localStorage.setItem("telemetry-settings-v1", JSON.stringify(settings));
    } catch {
      /* Preferences are optional. */
    }
    for (const format of ["json", "csv", "html", "input"])
      element<HTMLAnchorElement>(`download-${format}`).href =
        `/api/report?${query}&format=${format}`;
    element("results").hidden = false;
    chart();
    evaluation();
    text(
      "status",
      `Complete · ${run.observations.length} frames · ${run.scenario} · training excluded from evaluation`,
    );
  } catch (error) {
    if (active !== generation || (error instanceof DOMException && error.name === "AbortError"))
      return;
    text(
      "status",
      "Analysis failed. Previous evidence is hidden. Check the local service and retry.",
    );
    element("retry").hidden = false;
  } finally {
    if (active === generation) element<HTMLButtonElement>("apply").disabled = false;
  }
}
/** Update finite controls without silently relabeling the last completed analysis. */
function configure(value: Settings): void {
  for (const [key, entry] of Object.entries(value))
    element<HTMLSelectElement>(key).value = String(entry);
  text("scenario-description", catalog.scenarios[value.scenario] ?? "");
}
/** Initialize reviewed options, restore safe preferences and wire analysis/inspection controls. */
async function start(): Promise<void> {
  try {
    const response = await fetch("/api/catalog");
    if (!response.ok) throw new Error("Catalog unavailable");
    catalog = (await response.json()) as Catalog;
    for (const name of Object.keys(catalog.scenarios))
      element("scenario").append(new Option(name.replaceAll("-", " "), name));
    for (const [key, values] of Object.entries(catalog.choices))
      for (const value of values)
        element(key).append(
          new Option(
            key === "contextual" ? (value ? "Context-aware" : "Pooled") : String(value),
            String(value),
          ),
        );
    let raw: string | null = null;
    try {
      raw = localStorage.getItem("telemetry-settings-v1");
    } catch {
      /* Optional storage. */
    }
    configure(preferences(raw, catalog));
    element("config").addEventListener("submit", (event) => {
      event.preventDefault();
      void load();
    });
    element("scenario").addEventListener("change", () =>
      text(
        "scenario-description",
        catalog.scenarios[element<HTMLSelectElement>("scenario").value] ?? "",
      ),
    );
    element("reset").addEventListener("click", () => {
      configure(catalog.defaults);
      void load();
    });
    element("retry").addEventListener("click", () => void load());
    element("channel").addEventListener("change", chart);
    element("labels").addEventListener("change", chart);
    element("ledger-filter").addEventListener("change", ledger);
    element("tick").addEventListener("input", () => {
      tick = Number(element<HTMLInputElement>("tick").value);
      inspect();
    });
    window.addEventListener("pagehide", () => controller?.abort());
    await load();
  } catch {
    text("status", "Cannot load local configuration. Restart the service, then reload this page.");
  }
}
void start();
