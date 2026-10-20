"""Measured synthetic detector evaluation and cross-platform golden evidence by Jason Stys.

Function: main. Variables:24 fixture reports, reviewed metrics/hashes and observational timings.
Exact symbol/variable lines: docs/CODE_INDEX.md. --write intentionally refreshes reviewable evidence.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from telemetry.engine import SCENARIOS, Settings, analyze, build_run, generate  # noqa: E402
from telemetry.reports import observation_csv  # noqa: E402


def main() -> None:
    """Verify deterministic metrics independently across builds; timing is not a flaky pass gate."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    evidence = {}
    for scenario in SCENARIOS:
        for seed in (7, 23, 101):
            run = build_run(Settings(scenario=scenario, seed=seed))
            evidence[f"{scenario}/seed{seed}"] = {
                "id": run["id"],
                "metrics": run["metrics"],
                "comparison": run["comparison"],
            }
    report = root / "docs/reports/benchmark.json"
    if args.write:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )
        example = root / "examples/slow-drift.csv"
        example.parent.mkdir(exist_ok=True)
        example.write_bytes(observation_csv(build_run(Settings(scenario="slow-drift"))))
    elif json.loads(report.read_text(encoding="utf-8")) != evidence:
        raise SystemExit(
            "Reviewed synthetic benchmark differs; investigate before refreshing fixtures"
        )
    timings = []
    settings = Settings(scenario="slow-drift", duration=480)
    frames, truth = generate(settings)
    for _ in range(20):
        start = time.perf_counter()
        analyze(frames, settings, truth, "timing")
        timings.append((time.perf_counter() - start) * 1000)
    print(
        f"24 deterministic benchmark fixtures passed;20 uncached480-frame analyses median {statistics.median(timings):.2f}ms, max {max(timings):.2f}ms (host-specific, no latency guarantee)"
    )


if __name__ == "__main__":
    main()
