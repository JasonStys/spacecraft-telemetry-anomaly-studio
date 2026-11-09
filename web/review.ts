/* Run-bound human annotations by Jason Stys. Function: reviewDocument; variables: allowed statuses,
 * episode IDs and bounded plain-text notes. No detector/truth edits. Exact lines: docs/CODE_INDEX.md.
 */
import type { Run } from "./types";
export interface Annotation {
  status: string;
  note: string;
}
/** Export only annotations of this evidence run; unknown episode IDs and statuses fail closed. */
export function reviewDocument(run: Run, annotations: Record<string, Annotation>): object {
  const ids = new Set(run.episodes.map((episode) => episode.id));
  for (const [id, annotation] of Object.entries(annotations)) {
    if (
      !ids.has(id) ||
      !["unreviewed", "investigate", "explained", "uncertain"].includes(annotation.status) ||
      typeof annotation.note !== "string" ||
      annotation.note.length > 1000
    )
      throw new Error("Invalid run-bound annotation");
  }
  return {
    schema: "telemetry-human-review-v1",
    run_sha256: run.id,
    scope:
      "Human observations, not ground truth or a detector override. Notes stay in this tab until exported.",
    episodes: run.episodes.map((episode) => ({
      ...episode,
      annotation: annotations[episode.id] ?? { status: "unreviewed", note: "" },
    })),
  };
}
