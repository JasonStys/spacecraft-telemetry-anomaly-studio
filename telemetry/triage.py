"""Run-derived alert episode boundaries by Jason Stys.

Function: episodes. Variables: channel-local active episode, previous observation and boundaries.
This groups existing decisions without changing detector state or labels. Lines: docs/CODE_INDEX.md.
"""

from typing import Any


def episodes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group consecutive channel alerts; missing/context/window boundaries censor continuity.

    End ticks are the last observed alert, not the later boundary tick. Recovery is an observed
    non-alert in the same mode. All other ends are right-censored; starts after a missing value,
    mode change or the scoring-window start are left-censored. Duration counts observed alerts.
    """
    result: list[dict[str, Any]] = []
    if not rows:
        return result
    for channel_index, channel in enumerate(rows[0]["channels"]):
        active: dict[str, Any] | None = None
        previous: dict[str, Any] | None = None
        for row in rows:
            decision = row["channels"][channel_index]
            boundary = (
                "mode-change"
                if previous is not None and row["mode"] != previous["mode"]
                else "gap"
                if decision["value"] is None
                else "recovery"
                if not decision["reasons"]
                else None
            )
            if active is not None and boundary is not None:
                active["end_boundary"] = boundary
                active["right_censored"] = boundary != "recovery"
                result.append(active)
                active = None
            if decision["value"] is not None and decision["reasons"]:
                if active is None:
                    start_boundary = (
                        "scoring-window-start"
                        if previous is None
                        else "mode-change"
                        if row["mode"] != previous["mode"]
                        else "gap"
                        if previous["channels"][channel_index]["value"] is None
                        else "observed-onset"
                    )
                    active = {
                        "id": f"{channel['channel']}:{row['tick']}:{row['mode']}",
                        "channel": channel["channel"],
                        "mode": row["mode"],
                        "start_tick": row["tick"],
                        "end_tick": row["tick"],
                        "observed_ticks": 0,
                        "reasons": [],
                        "peak_absolute_score": 0.0,
                        "start_boundary": start_boundary,
                        "left_censored": start_boundary != "observed-onset",
                    }
                active["end_tick"] = row["tick"]
                active["observed_ticks"] += 1
                active["reasons"] = sorted(set(active["reasons"]) | set(decision["reasons"]))
                active["peak_absolute_score"] = max(
                    active["peak_absolute_score"], abs(decision["score"] or 0.0)
                )
            previous = row
        if active is not None:
            active["end_boundary"] = "scoring-window-end"
            active["right_censored"] = True
            result.append(active)
    return sorted(result, key=lambda item: (item["start_tick"], item["channel"]))
