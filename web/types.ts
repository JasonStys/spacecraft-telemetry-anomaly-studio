/* Telemetry UI schema by Jason Stys. Interfaces: Settings, Catalog, Frame, Decision, Row, Run.
 * Field definitions and source line inventory: docs/CODE_INDEX.md. Null means absence/undefined.
 */
export interface Settings {
  scenario: string;
  duration: number;
  fault_tick: number;
  seed: number;
  threshold: number;
  contextual: number;
}
export interface Catalog {
  scenarios: Record<string, string>;
  choices: Record<string, number[]>;
  defaults: Settings;
  channels: string[];
  training: number;
}
export interface Frame {
  tick: number;
  mode: string;
  values: (number | null)[];
}
export interface Decision {
  channel: string;
  value: number | null;
  center: number;
  lower: number;
  upper: number;
  score: number | null;
  drift: number | null;
  repeats: number;
  reasons: string[];
}
export interface Row {
  tick: number;
  mode: string;
  channels: Decision[];
}
export type Metrics = Record<string, number | null>;
export interface Run {
  id: string;
  scenario: string;
  settings: Settings;
  observations: Frame[];
  rows: Row[];
  truth: Record<string, string[]> | null;
  model: Record<string, { center: number; scale: number }[]>;
  metrics: Metrics;
  comparison: Metrics;
  provenance: {
    training_ticks: number[];
    evaluation_ticks: number[];
    source: string;
    algorithm: string;
  };
}
