# Review alert episodes

The analyst triage panel groups existing detector flags into consecutive episodes per channel and mode. It does not refit the model, use evaluation labels, or change a decision. JSON/HTML evidence and CLI history include the episode ledger inside the run hash.

An episode ends at its last observed flagged tick. The following non-alert in the same mode proves **observed recovery**. A missing observation, context change or scoring-window end instead **censors** continuity: recovery was not observed. Starts at the scoring-window edge or after a gap/context change are also marked censored. Duration counts observed flagged ticks, not a guessed fault lifetime. Peak absolute score is a standardized detector residual, not a physical severity measure.

Select a review status and enter up to 1,000 characters of plain text per episode. Download human review JSON before analyzing another configuration. The export binds the run SHA-256 and the original episode boundaries to the analyst's notes. Notes stay in the current tab, are never uploaded, and reset on a new analysis. They are human observations, not truth labels, diagnoses or a detector override. The app does not import reviews or authenticate reviewers; share the evidence and review together using your own trusted process.

Try isolated spike (one observed recovery), then step shift and missing-value fixtures. Local CSV imports retain unknown accuracy metrics and use exactly the same grouping rules. This is an educational single-analyst tool with no operational spacecraft connection.
