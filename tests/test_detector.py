"""Independent robust-statistic, causal and edge-case contracts by Jason Stys.

Functions: training fixture and test_* oracles. Variables: hand-computed medians/MAD, observed
prefix, future mutations and missing-frame boundaries. Exact lines: docs/CODE_INDEX.md.
"""

import math
from dataclasses import replace
from itertools import product

import pytest
from hypothesis import given
from hypothesis import settings as hs
from hypothesis import strategies as st

from telemetry.detector import Band, Detector, Frame, fit, validate_frames
from telemetry.engine import (
    CHOICES,
    SCENARIOS,
    Settings,
    analyze,
    build_run,
    catalog,
    generate,
    metrics,
    run_id,
)


def training():
    """Supply a manually constructed prefix with two characterized contexts and known robust scale."""
    return [Frame(i, "SUNLIT" if i < 40 else "ECLIPSE", (float(i % 5),) * 3) for i in range(80)]


def test_median_mad_oracle():
    """For repeated0..4, center2 and median deviation1 are independently known."""
    model = fit(training(), True)
    assert model["SUNLIT"][0] == Band(2.0, 1.4826)
    assert fit(training(), False)["POOLED"][0] == Band(2.0, 1.4826)
    constant = [replace(frame, values=(7.0,) * 3) for frame in training()]
    assert fit(constant, True)["SUNLIT"][0] == Band(7.0, 1.0)


def test_exact_rule_boundaries():
    """Point comparison is strict >; drift follows alpha0.2; six repeats flags only at the sixth."""
    model = {mode: (Band(0.0, 1.0),) * 3 for mode in ("SUNLIT", "ECLIPSE")}
    detector = Detector(model, 4, True)
    first = detector.observe(Frame(80, "SUNLIT", (4.0, 0.0, 0.0)))["channels"][0]
    assert first["score"] == 4 and first["drift"] == 0.8 and first["reasons"] == []
    second = detector.observe(Frame(81, "SUNLIT", (5.0, 0.0, 0.0)))["channels"][0]
    assert second["drift"] == 1.64 and second["reasons"] == ["point-limit"]
    flat = Detector(model, 4, True)
    for tick in range(80, 85):
        assert (
            "flatline"
            not in flat.observe(Frame(tick, "SUNLIT", (0.0,) * 3))["channels"][0]["reasons"]
        )
    assert flat.observe(Frame(85, "SUNLIT", (0.0,) * 3))["channels"][0]["reasons"] == ["flatline"]


def test_reset_and_context():
    """A missing value or context change clears temporal memory rather than imputing zero."""
    detector = Detector(fit(training(), True), 4, True)
    for tick in range(80, 85):
        detector.observe(Frame(tick, "SUNLIT", (2.0,) * 3))
    missing = detector.observe(Frame(85, "SUNLIT", (None, 2.0, 2.0)))["channels"][0]
    assert (
        missing["score"] is None
        and missing["drift"] is None
        and missing["repeats"] == 0
        and not missing["reasons"]
    )
    assert detector.observe(Frame(86, "SUNLIT", (2.0,) * 3))["channels"][0]["repeats"] == 1
    assert detector.observe(Frame(87, "ECLIPSE", (2.0,) * 3))["channels"][0]["repeats"] == 1
    with pytest.raises(ValueError):
        detector.observe(Frame(89, "ECLIPSE", (2.0,) * 3))


def test_causality_and_label_isolation():
    """Changing future observations or evaluation labels cannot alter earlier decisions/trained bands."""
    settings = Settings(scenario="slow-drift")
    frames, truth = generate(settings)
    first = analyze(frames, settings, truth, "test")
    changed = list(frames)
    changed[200] = replace(changed[200], values=(9999.0,) * 3)
    second = analyze(changed, settings, {i: set() for i in truth}, "test")
    assert first["model"] == second["model"]
    assert first["rows"][:120] == second["rows"][:120]
    unchanged = analyze(frames, settings, {i: set() for i in truth}, "test")
    assert first["rows"] == unchanged["rows"] and first["metrics"] != unchanged["metrics"]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_default_scenario_contracts(scenario):
    """Known synthetic durations/counts are checked independently of saved metric snapshots."""
    run = build_run(Settings(scenario=scenario))
    result = run["metrics"]
    assert run["id"] == run_id(run) and len(run["rows"]) == 160 and len(run["observations"]) == 240
    assert result["observed"] + result["missing"] == 480
    assert sum(result[k] for k in ("tp", "fp", "fn", "tn")) == result["observed"]
    if scenario == "nominal":
        assert result["alerts"] == 0 and result["precision"] is None and result["recall"] is None
    elif scenario == "isolated-spike":
        assert result["tp"] == 1 and result["fp"] == 0 and result["delay"] == 0
    elif scenario == "multichannel-burst":
        assert result["tp"] + result["fn"] == 24 and result["fp"] > 0
    elif scenario == "slow-drift":
        assert result["tp"] + result["fn"] == 36 and result["delay"] > 0
    elif scenario == "stuck-sensor":
        assert result["delay"] == 5 and result["tp"] + result["fn"] == 36
    elif scenario == "telemetry-gap":
        assert result["missing"] == 36 and result["alerts"] == 0
    elif scenario == "partial-dropout":
        assert result["missing"] == 12 and result["alerts"] == 0
    else:
        assert result["tp"] == 36


def test_full_config_grid():
    """Exercise all576 finite scenario/parameter combinations without retaining mutable reports."""
    count = 0
    for scenario, values in product(SCENARIOS, product(*CHOICES.values())):
        settings = Settings(scenario, *values)
        frames, truth = generate(settings)
        assert (
            frames[:80]
            == generate(Settings(scenario="nominal", **{k: getattr(settings, k) for k in CHOICES}))[
                0
            ][:80]
        )
        run = analyze(frames, settings, truth, "grid")
        assert (
            run["metrics"]["observed"] + run["metrics"]["missing"] == (settings.duration - 80) * 3
        )
        assert run["metrics"]["tp"] + run["metrics"]["fn"] == sum(len(v) for v in truth.values())
        count += 1
    assert count == 576


@given(st.sampled_from(list(SCENARIOS)), st.sampled_from((7, 23, 101)), st.sampled_from((3, 4, 6)))
@hs(max_examples=30, deadline=None)
def test_detached_deterministic_results(scenario, seed, threshold):
    """Canonical results repeat and cached data cannot be poisoned by caller mutation."""
    settings = Settings(scenario=scenario, seed=seed, threshold=threshold)
    run = build_run(settings)
    assert run == build_run(settings)
    run["rows"][0]["channels"][0]["reasons"].append("poison")
    assert "poison" not in build_run(settings)["rows"][0]["channels"][0]["reasons"]


@pytest.mark.parametrize(
    "key,value",
    [
        ("scenario", []),
        ("scenario", "unknown"),
        ("duration", True),
        ("duration", 240.0),
        ("duration", -1),
        ("fault_tick", 20),
        ("seed", 0),
        ("threshold", 0),
        ("contextual", 2),
    ],
)
def test_invalid_settings(key, value):
    """Only exact reviewed primitives are accepted; no boolean-as-integer coercion."""
    with pytest.raises(ValueError):
        Settings(**{key: value})


@pytest.mark.parametrize(
    "frame",
    [
        (-1, "SUNLIT", (1.0,) * 3),
        (True, "SUNLIT", (1.0,) * 3),
        (480, "SUNLIT", (1.0,) * 3),
        (0, "unknown", (1.0,) * 3),
        (0, "SUNLIT", (1.0,)),
        (0, "SUNLIT", (math.nan, 1.0, 1.0)),
        (0, "SUNLIT", (math.inf, 1.0, 1.0)),
        (0, "SUNLIT", (10001.0, 1.0, 1.0)),
        (0, "SUNLIT", (True, 1.0, 1.0)),
    ],
)
def test_invalid_frames(frame):
    """Reject grid bounds, unsupported context, bad arity, booleans and nonfinite values."""
    with pytest.raises(ValueError):
        Frame(*frame)


def test_bad_training_models_and_metrics():
    """Insufficient/contaminated-quality prefixes and invalid bands fail explicitly."""
    with pytest.raises(ValueError):
        validate_frames(training())
    with pytest.raises(ValueError):
        fit(training()[:79], True)
    with pytest.raises(ValueError):
        fit([replace(f, values=(None,) * 3) for f in training()], True)
    with pytest.raises(ValueError):
        fit([replace(f, mode="SUNLIT") for f in training()], True)
    with pytest.raises(ValueError):
        Detector({}, 4, True)
    with pytest.raises(ValueError):
        Detector({"POOLED": (Band(0.0, math.inf),) * 3}, 4, False)
    with pytest.raises(ValueError):
        Detector({"POOLED": (Band(0.0, 0.0),) * 3}, 4, False)
    assert metrics([], None)["tp"] is None and metrics([], {})["precision"] is None
    assert catalog()["training"] == 80
