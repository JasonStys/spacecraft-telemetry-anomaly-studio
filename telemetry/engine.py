"""Synthetic fixtures, label-isolated analysis and honest metrics by Jason Stys.

Classes/functions: Settings, generate, analyze, metrics, build_run, build_import, run_id.
Variables: scenario settings, frozen training boundary, held-out truth and detached cached JSON.
Exact lines: docs/CODE_INDEX.md. No spacecraft command, dynamics or hardware interface exists.
"""

import csv
import hashlib
import io
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from telemetry.detector import CHANNELS, MODES, TRAINING, Detector, Frame, fit, validate_frames

SCENARIOS = {
    "nominal": "Healthy context transitions; no injected sensor anomaly",
    "isolated-spike": "One thermal-index spike at the injection tick",
    "multichannel-burst": "Twelve ticks of concurrent bus/load shifts",
    "slow-drift": "Thirty-six ticks of gradually increasing thermal bias",
    "stuck-sensor": "Thirty-six ticks of a frozen thermal reading",
    "telemetry-gap": "Twelve entirely missing frames; quality issue, not a sensor anomaly",
    "partial-dropout": "Twelve missing bus readings while other channels remain observable",
    "step-shift": "Thirty-six ticks of an abrupt thermal-index bias",
}
CHOICES = {
    "duration": (240, 480),
    "fault_tick": (120, 160),
    "seed": (7, 23, 101),
    "threshold": (3, 4, 6),
    "contextual": (0, 1),
}


@dataclass(frozen=True)
class Settings:
    """Finite synthetic experiment; threshold is a multiplier, not a probability/confidence level."""

    scenario: str = "isolated-spike"
    duration: int = 240
    fault_tick: int = 120
    seed: int = 7
    threshold: int = 4
    contextual: int = 1

    def __post_init__(self) -> None:
        """Refuse coercion, arbitrary workloads and faults inside the fixed training prefix."""
        if type(self.scenario) is not str or self.scenario not in SCENARIOS:
            raise ValueError("Unknown scenario")
        for key, choices in CHOICES.items():
            value = getattr(self, key)
            if type(value) is not int or value not in choices:
                raise ValueError(f"Unsupported {key}")


def catalog() -> dict[str, Any]:
    """Return reviewed choices, channel/context contracts and a fixed training boundary."""
    return {
        "scenarios": SCENARIOS,
        "choices": CHOICES,
        "defaults": asdict(Settings()),
        "channels": CHANNELS,
        "training": TRAINING,
    }


def canonical(value: Any) -> bytes:
    """Encode stable sorted finite JSON for reports, detached caching and content hashes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def run_id(run: dict[str, Any]) -> str:
    """Hash every evidence field except the self-referential id; hashes are not signatures."""
    return hashlib.sha256(canonical({k: v for k, v in run.items() if k != "id"})).hexdigest()


def generate(settings: Settings) -> tuple[list[Frame], dict[int, set[str]]]:
    """Generate invented indices from a fixed integer PRNG; keep truth outside the observation model."""
    random = settings.seed
    frames = []
    truth: dict[int, set[str]] = {}
    frozen: float | None = None
    for tick in range(settings.duration):
        mode = MODES[0] if tick % 40 < 24 else MODES[1]
        centers = (500, 780, 250) if mode == MODES[0] else (390, 750, 180)
        nominal: list[float] = []
        for center in centers:
            random = (1664525 * random + 1013904223) & 0xFFFFFFFF
            nominal.append(float(center + ((random >> 16) % 9) - 4))
        values: list[float | None] = list(nominal)
        elapsed = tick - settings.fault_tick
        affected: set[str] = set()
        if elapsed == 0:
            frozen = values[0]
        if settings.scenario == "isolated-spike" and elapsed == 0:
            values[0] = nominal[0] + 40
            affected.add("thermal")
        if settings.scenario == "multichannel-burst" and 0 <= elapsed < 12:
            values[1], values[2] = nominal[1] - 28, nominal[2] + 32
            affected.update(("bus", "load"))
        if settings.scenario in {"slow-drift", "step-shift"} and 0 <= elapsed < 36:
            values[0] = nominal[0] + (elapsed + 1 if settings.scenario == "slow-drift" else 24)
            affected.add("thermal")
        if settings.scenario == "stuck-sensor" and 0 <= elapsed < 36:
            values[0] = frozen
            affected.add("thermal")
        if settings.scenario == "telemetry-gap" and 0 <= elapsed < 12:
            values = [None, None, None]
        if settings.scenario == "partial-dropout" and 0 <= elapsed < 12:
            values[1] = None
        frames.append(Frame(tick, mode, tuple(values)))
        truth[tick] = affected
    return frames, truth


def metrics(rows: list[dict[str, Any]], truth: dict[int, set[str]] | None) -> dict[str, Any]:
    """Evaluate observed channel-ticks only; null denominators/unknown labels remain undefined."""
    result: dict[str, Any] = {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "observed": 0,
        "missing": 0,
        "alerts": 0,
        "precision": None,
        "recall": None,
        "f1": None,
        "delay": None,
    }
    first_truth: int | None = None
    first_detection: int | None = None
    for row in rows:
        for channel in row["channels"]:
            name, value = channel["channel"], channel["value"]
            if value is None:
                result["missing"] += 1
                continue
            result["observed"] += 1
            predicted = bool(channel["reasons"])
            result["alerts"] += predicted
            if truth is not None:
                actual = name in truth[row["tick"]]
                result[
                    "tp"
                    if predicted and actual
                    else "fp"
                    if predicted
                    else "fn"
                    if actual
                    else "tn"
                ] += 1
                if actual and first_truth is None:
                    first_truth = row["tick"]
                if actual and predicted and first_detection is None:
                    first_detection = row["tick"]
    if truth is not None:
        precision_denominator = result["tp"] + result["fp"]
        recall_denominator = result["tp"] + result["fn"]
        result["precision"] = (
            round(result["tp"] / precision_denominator, 6) if precision_denominator else None
        )
        result["recall"] = (
            round(result["tp"] / recall_denominator, 6) if recall_denominator else None
        )
        f1_denominator = 2 * result["tp"] + result["fp"] + result["fn"]
        result["f1"] = round(2 * result["tp"] / f1_denominator, 6) if f1_denominator else None
        result["delay"] = (
            first_detection - first_truth
            if first_detection is not None and first_truth is not None
            else None
        )
    else:
        for key in ("tp", "fp", "fn", "tn"):
            result[key] = None
    return result


def analyze(
    frames: list[Frame], settings: Settings, truth: dict[int, set[str]] | None, source: str
) -> dict[str, Any]:
    """Fit on ticks0..79 then score causally; evaluation labels enter only the metric step."""
    validate_frames(frames)
    training = frames[:TRAINING]
    model = fit(training, bool(settings.contextual))
    detector = Detector(model, settings.threshold, bool(settings.contextual))
    rows = [detector.observe(frame) for frame in frames[TRAINING:]]
    alternate = Detector(
        fit(training, not bool(settings.contextual)),
        settings.threshold,
        not bool(settings.contextual),
    )
    comparison = [alternate.observe(frame) for frame in frames[TRAINING:]]
    run = {
        "schema": 1,
        "scenario": settings.scenario if truth is not None else "local-csv",
        "settings": asdict(settings)
        if truth is not None
        else {
            "duration": len(frames),
            "threshold": settings.threshold,
            "contextual": settings.contextual,
        },
        "observations": [asdict(frame) for frame in frames],
        "rows": rows,
        "truth": {str(tick): sorted(channels) for tick, channels in truth.items()}
        if truth is not None
        else None,
        "model": {mode: [asdict(band) for band in bands] for mode, bands in model.items()},
        "metrics": metrics(rows, truth),
        "comparison": metrics(comparison, truth),
        "provenance": {
            "author": "Jason Stys",
            "version": "1.0.0",
            "algorithm": "median-MAD + causal EWMA + six-repeat flatline",
            "clock": "logical ticks",
            "training_ticks": [0, 79],
            "evaluation_ticks": [80, len(frames) - 1],
            "source": source,
            "units": "Synthetic index (or locally mapped CSV values); not physical spacecraft measurements",
            "scope": "Teaching analysis only; no operational or flight assurance",
        },
    }
    run["id"] = run_id(run)
    return run


@lru_cache(maxsize=24)
def cached(settings: Settings) -> bytes:
    """Cache only immutable serialized results; no caller can mutate another user's result."""
    frames, truth = generate(settings)
    return canonical(analyze(frames, settings, truth, "seeded-synthetic"))


def build_run(settings: Settings) -> dict[str, Any]:
    """Return detached evidence for one finite reviewed synthetic fixture."""
    return json.loads(cached(settings))  # type: ignore[no-any-return]


def read_csv(payload: bytes) -> list[Frame]:
    """Read only a bounded UTF-8 numeric schema; no formulas, archives, scripts or path resolution."""
    if len(payload) > 256000:
        raise ValueError("CSV exceeds256000bytes")
    try:
        reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), strict=True)
        if reader.fieldnames != ["tick", "mode", *CHANNELS]:
            raise ValueError("Expected tick,mode,thermal,bus,load header")
        frames: list[Frame] = []
        for row in reader:
            if (
                len(frames) >= 480
                or set(row) != {"tick", "mode", *CHANNELS}
                or any(v is None for v in row.values())
            ):
                raise ValueError("Malformed or excessive CSV rows")
            frames.append(
                Frame(
                    int(row["tick"]),
                    row["mode"],
                    tuple(
                        float(row[channel]) if row[channel].strip() else None
                        for channel in CHANNELS
                    ),
                )
            )
        validate_frames(frames)
        return frames
    except (UnicodeError, csv.Error, TypeError) as error:
        raise ValueError("Invalid UTF-8 numeric telemetry CSV") from error


def build_import(path: Path, settings: Settings) -> dict[str, Any]:
    """CLI-only local import; read at most cap+1 bytes and never include the user's path in evidence."""
    with path.open("rb") as source:
        frames = read_csv(source.read(256001))
    return analyze(
        frames, settings, None, "local-csv; training prefix assumed clean, labels unknown"
    )
