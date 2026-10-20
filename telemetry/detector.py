"""Causal robust limits, drift and flatline detection by Jason Stys.

Classes: Frame, Band, Detector. Functions: fit, validate_frames. Variables: immutable training
bands, per-channel EWMA/repeat state and observed-only decisions. Lines: docs/CODE_INDEX.md.
No evaluation labels, future frames, external models or flight interfaces enter the detector.
"""

import math
from dataclasses import dataclass
from statistics import median
from typing import Any

CHANNELS = ("thermal", "bus", "load")
MODES = ("SUNLIT", "ECLIPSE")
TRAINING = 80


@dataclass(frozen=True)
class Frame:
    """One logical observation; None is absence, never a measured zero or carried-forward value."""

    tick: int
    mode: str
    values: tuple[float | None, ...]

    def __post_init__(self) -> None:
        """Enforce the compact input schema before any arithmetic, including direct callers."""
        if type(self.tick) is not int or not 0 <= self.tick < 480 or self.mode not in MODES:
            raise ValueError("Invalid frame clock or context")
        if len(self.values) != len(CHANNELS):
            raise ValueError("Expected exactly three channels")
        for value in self.values:
            if value is not None and (
                type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 10000
            ):
                raise ValueError("Nonfinite or unbounded channel value")


@dataclass(frozen=True)
class Band:
    """Frozen training-only center and robust scale; floor1 avoids division by zero."""

    center: float
    scale: float


def validate_frames(frames: list[Frame]) -> None:
    """Require a complete bounded logical grid; missing values belong inside frames."""
    if len(frames) not in (240, 480) or any(frame.tick != i for i, frame in enumerate(frames)):
        raise ValueError("Expected 240 or 480 ordered frames starting at tick0")


def fit(training: list[Frame], contextual: bool) -> dict[str, tuple[Band, ...]]:
    """Fit only an explicit clean-prefix assumption; no future frames or truth labels are accepted."""
    if len(training) != TRAINING or any(f.tick != i for i, f in enumerate(training)):
        raise ValueError("Expected the first80 ordered training frames")
    if any(value is None for f in training for value in f.values):
        raise ValueError("Training prefix must contain every channel observation")
    # Require both contexts even for pooled comparison, so all supported modes are characterized.
    if any(sum(f.mode == mode for f in training) < 12 for mode in MODES):
        raise ValueError("Training needs at least12 observations of each context")
    model = {}
    for mode in MODES if contextual else ("POOLED",):
        rows = [f for f in training if not contextual or f.mode == mode]
        bands = []
        for channel in range(len(CHANNELS)):
            values = [value for f in rows if (value := f.values[channel]) is not None]
            center = median(values)
            mad = median(abs(value - center) for value in values)
            bands.append(Band(center, max(1.0, 1.4826 * mad)))
        model[mode] = tuple(bands)
    return model


class Detector:
    """Stateful one-frame-at-a-time scorer; use one owner per independent analysis."""

    def __init__(self, model: dict[str, tuple[Band, ...]], threshold: int, contextual: bool):
        """Accept only the finite reviewed sensitivity and complete fitted model schema."""
        expected = set(MODES) if contextual else {"POOLED"}
        if type(threshold) is not int or threshold not in (3, 4, 6) or set(model) != expected:
            raise ValueError("Unsupported detector configuration")
        for bands in model.values():
            if len(bands) != 3 or any(
                not math.isfinite(b.center) or not math.isfinite(b.scale) or b.scale < 1
                for b in bands
            ):
                raise ValueError("Invalid model bands")
        self.model = dict(model)
        self.threshold = threshold
        self.contextual = contextual
        self.ewma = [0.0] * 3
        self.previous: list[float | None] = [None] * 3
        self.repeats = [0] * 3
        self.mode = ""
        self.last_tick = TRAINING - 1

    def observe(self, frame: Frame) -> dict[str, Any]:
        """Score causally; absence/context changes reset temporal memory, never impute a value."""
        if frame.tick != self.last_tick + 1:
            raise ValueError("Scoring requires consecutive post-training frames")
        self.last_tick = frame.tick
        if frame.mode != self.mode:
            self.ewma = [0.0] * 3
            self.previous = [None] * 3
            self.repeats = [0] * 3
            self.mode = frame.mode
        bands = self.model[frame.mode if self.contextual else "POOLED"]
        decisions = []
        for index, (name, value, band) in enumerate(
            zip(CHANNELS, frame.values, bands, strict=True)
        ):
            reasons = []
            score: float | None = None
            drift: float | None = None
            if value is None:
                self.ewma[index] = 0
                self.previous[index] = None
                self.repeats[index] = 0
            else:
                score = (value - band.center) / band.scale
                self.ewma[index] = 0.2 * score + 0.8 * self.ewma[index]
                drift = self.ewma[index]
                self.repeats[index] = (
                    self.repeats[index] + 1 if value == self.previous[index] else 1
                )
                self.previous[index] = value
                if abs(score) > self.threshold:
                    reasons.append("point-limit")
                if abs(drift) > 0.6 * self.threshold:
                    reasons.append("drift")
                if self.repeats[index] >= 6:
                    reasons.append("flatline")
            decisions.append(
                {
                    "channel": name,
                    "value": value,
                    "center": band.center,
                    "lower": round(band.center - self.threshold * band.scale, 6),
                    "upper": round(band.center + self.threshold * band.scale, 6),
                    "score": round(score, 6) if score is not None else None,
                    "drift": round(drift, 6) if drift is not None else None,
                    "repeats": self.repeats[index],
                    "reasons": reasons,
                }
            )
        return {"tick": frame.tick, "mode": frame.mode, "channels": decisions}
