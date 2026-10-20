"""Bounded local numeric CSV, undefined imported metrics and parser fuzz tests by Jason Stys.

Functions: test_*; variables: strict fixture payloads, malformed schemas and arbitrary bytes.
Source index: docs/CODE_INDEX.md. No untrusted code or archived artifact is executed.
"""

import pytest
from hypothesis import given
from hypothesis import settings as hs
from hypothesis import strategies as st

from telemetry.__main__ import main
from telemetry.engine import Settings, build_import, build_run, generate, read_csv
from telemetry.reports import observation_csv


def test_import_roundtrip_and_cli(tmp_path):
    """Strict exported observations round-trip; imported labels and accuracy are explicitly unknown."""
    settings = Settings(scenario="partial-dropout", duration=480)
    run = build_run(settings)
    payload = observation_csv(run)
    assert read_csv(payload) == generate(settings)[0]
    source = tmp_path / "private-name.csv"
    source.write_bytes(payload)
    imported = build_import(source, Settings())
    assert imported["scenario"] == "local-csv" and imported["settings"]["duration"] == 480
    assert (
        imported["truth"] is None
        and imported["metrics"]["recall"] is None
        and imported["metrics"]["tp"] is None
    )
    assert imported["metrics"]["missing"] == 12 and "private-name" not in str(imported)
    assert main(["export", "--input", str(source), "--output", str(tmp_path / "result.json")]) == 0


@pytest.mark.parametrize(
    "payload",
    [
        b"x" * 256001,
        b"\xff",
        b"tick,mode,thermal,bus,load\n0,SUNLIT,NaN,1,2\n",
        b"tick,mode,thermal,bus,load\n0,SUNLIT,=1,1,2\n",
        b"tick,mode,thermal,bus,load\n0,SUNLIT,1,1\n",
        b'tick,mode,thermal,bus,load\n0,"SUNLIT,1,1,1',
        b"tick,mode,thermal,bus,load,extra\n",
        b"tick,mode,thermal,bus,load\n0,SUNLIT,1,1,2,extra\n",
    ],
    ids=[
        "oversize",
        "bad-utf8",
        "nan",
        "formula",
        "short-row",
        "unclosed-quote",
        "extra-header",
        "extra-value",
    ],
)
def test_invalid_csv(payload):
    """Bad UTF-8/schema/size/numbers/arity/quoting is rejected without interpretation."""
    with pytest.raises(ValueError):
        read_csv(payload)


def test_csv_grid_limits():
    """Excessive or out-of-order logical clocks cannot silently sort, truncate or expand workload."""
    payload = observation_csv(build_run(Settings()))
    with pytest.raises(ValueError):
        read_csv(payload.replace(b"120,SUNLIT", b"119,SUNLIT"))
    long = observation_csv(build_run(Settings(duration=480))) + b"480,SUNLIT,1,2,3\n"
    with pytest.raises(ValueError):
        read_csv(long)


@given(st.binary(max_size=2048))
@hs(max_examples=100, deadline=None)
def test_parser_fuzz(payload):
    """Arbitrary byte strings either yield the exact validated schema or a controlled ValueError."""
    try:
        result = read_csv(payload)
        assert len(result) in (240, 480)
    except ValueError:
        pass
