"""Independent episode-boundary examples by Jason Stys.

Functions: row and test_*; variables: hand-authored observations, channel gaps and mode boundaries.
Exact lines: docs/CODE_INDEX.md. Human review never changes detector evidence.
"""

from typing import Any

from telemetry.engine import Settings, build_run, run_id
from telemetry.triage import episodes


def row(tick: int, value: float | None, flagged: bool = True, mode: str = "a") -> dict[str, Any]:
    """Create one scored channel independently of the detector implementation."""
    return {
        "tick": tick,
        "mode": mode,
        "channels": [
            {
                "channel": "thermal",
                "value": value,
                "score": value,
                "reasons": ["point-limit"] if flagged else [],
            }
        ],
    }


def test_gap_context_and_window_censoring() -> None:
    """Missing/context boundaries split alerts; only observed recovery closes conclusively."""
    rows = [
        row(80, 9),
        row(81, 8),
        row(82, None),
        row(83, 7),
        row(84, 6, mode="b"),
        row(85, 0, False, "b"),
        row(86, 8, mode="b"),
    ]
    result = episodes(rows)
    assert [(e["start_tick"], e["end_tick"], e["end_boundary"]) for e in result] == [
        (80, 81, "gap"),
        (83, 83, "mode-change"),
        (84, 84, "recovery"),
        (86, 86, "scoring-window-end"),
    ]
    assert [e["left_censored"] for e in result] == [True, True, True, False]
    assert [e["right_censored"] for e in result] == [True, True, False, True]
    assert result[0]["observed_ticks"] == 2
    assert result[0]["peak_absolute_score"] == 9


def test_empty_normal_and_channel_independence() -> None:
    """No alerts means no episodes; a second channel's gap does not censor the first."""
    assert episodes([]) == []
    assert episodes([row(80, 0, False)]) == []
    rows = [row(80, -8), row(81, -7), row(82, 0, False)]
    for index, item in enumerate(rows):
        item["channels"].append(
            {"channel": "bus", "value": None if index == 1 else 1, "score": 1, "reasons": []}
        )
    assert len(episodes(rows)) == 1
    assert episodes(rows)[0]["peak_absolute_score"] == 8


def test_run_evidence_contains_episodes_without_label_dependency() -> None:
    """Episode grouping enters the content hash; synthetic spike has a hand-known location."""
    run = build_run(Settings())
    assert run["id"] == run_id(run)
    assert [(e["channel"], e["start_tick"], e["end_tick"]) for e in run["episodes"]] == [
        ("thermal", 120, 120)
    ]
    assert run["episodes"][0]["end_boundary"] == "recovery"
