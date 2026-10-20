"""Portable reports, canonical CSV inputs and local immutable SQL history by Jason Stys.

Functions: export_report, observation_csv, save_history. Variables: fixed formats/columns and
content-verified records. No uploads or user text formulas; exact lines: docs/CODE_INDEX.md.
"""

import csv
import io
import json
import sqlite3
from contextlib import closing
from html import escape
from importlib.resources import files
from pathlib import Path
from typing import Any

from telemetry.detector import CHANNELS
from telemetry.engine import run_id


def observation_csv(run: dict[str, Any]) -> bytes:
    """Export the exact strict CLI import schema with blanks for missing observations."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("tick", "mode", *CHANNELS))
    for frame in run["observations"]:
        writer.writerow((frame["tick"], frame["mode"], *frame["values"]))
    return stream.getvalue().encode()


def export_report(run: dict[str, Any], format_name: str) -> tuple[bytes, str]:
    """Serialize generated analysis; evidence CSV has explicit quality and evaluation labels."""
    if format_name == "json":
        return (json.dumps(run, indent=2, allow_nan=False) + "\n").encode(), "application/json"
    if format_name == "input":
        return observation_csv(run), "text/csv"
    if format_name == "csv":
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            (
                "run_sha256",
                "tick",
                "mode",
                "channel",
                "value",
                "center",
                "lower",
                "upper",
                "score",
                "drift",
                "repeats",
                "reasons",
                "injected_label",
            )
        )
        for row in run["rows"]:
            for channel in row["channels"]:
                label = (
                    channel["channel"] in run["truth"][str(row["tick"])]
                    if run["truth"] is not None
                    else "unknown"
                )
                writer.writerow(
                    (
                        run["id"],
                        row["tick"],
                        row["mode"],
                        *(
                            channel[key]
                            for key in (
                                "channel",
                                "value",
                                "center",
                                "lower",
                                "upper",
                                "score",
                                "drift",
                                "repeats",
                            )
                        ),
                        "|".join(channel["reasons"]),
                        label,
                    )
                )
        return stream.getvalue().encode(), "text/csv"
    if format_name == "html":
        payload = escape(json.dumps(run, indent=2, allow_nan=False))
        return (
            "<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width'>"
            "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'\">"
            "<title>Telemetry anomaly evidence</title><h1>Telemetry anomaly evidence</h1>"
            "<p>By Jason Stys. Teaching analysis only; synthetic or locally mapped data, no operational assurance.</p>"
            f"<pre>{payload}</pre></html>"
        ).encode(), "text/html"
    raise ValueError("Expected json, csv, html or input")


def save_history(path: Path, run: dict[str, Any]) -> str:
    """Save at most100 immutable local records; CLI-only path, no deletion or overwrite."""
    if run.get("id") != run_id(run):
        raise ValueError("Run content hash does not match")
    schema = files("telemetry").joinpath("resources/history.sql").read_text(encoding="utf-8")
    with closing(sqlite3.connect(path, timeout=5)) as connection, connection:
        connection.executescript(schema)
        connection.execute("BEGIN IMMEDIATE")
        exists = connection.execute("SELECT 1 FROM runs WHERE id = ?", (run["id"],)).fetchone()
        if not exists:
            count = connection.execute("SELECT count(*) FROM runs").fetchone()
            if count is not None and count[0] >= 100:
                raise ValueError("History full (100 runs); choose a new database")
            connection.execute(
                "INSERT INTO runs(id,scenario,report_json) VALUES (?,?,?)",
                (run["id"], run["scenario"], json.dumps(run, allow_nan=False)),
            )
    return str(run["id"])
