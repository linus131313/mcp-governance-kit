"""Paper-integrity tests: TCS of the reference configurations must exactly
reproduce Table 3 of the companion paper (§5.3 of governance-speed-gap).

If any of these tests fails, the tool no longer faithfully reproduces the
paper's numerical claims — treat as a release blocker.
"""

from __future__ import annotations

import pytest

from mcp_governance_kit.tcs import REFERENCE, tcs

# Expected values from governance-speed-gap/analysis/tcs_results.csv
# (paper Table 3). Keep decimals exact.
EXPECTED: dict[str, float] = {
    "C1": 1.0,
    "C2": 9.0,
    "C3": 13.5,
    "C4": 49.5,
    "C5": 29.75,
    "R1": 2.0,
    "R2": 5.0,
    "R3": 7.0,
    "R4": 15.0,
}


@pytest.mark.parametrize(("short", "expected"), list(EXPECTED.items()))
def test_reference_tcs_matches_paper(short: str, expected: float) -> None:
    [cfg] = [c for c in REFERENCE if c.short == short]
    assert tcs(cfg) == pytest.approx(expected, abs=1e-9), (
        f"{short}: expected {expected}, got {tcs(cfg)} — paper regression"
    )


def test_reference_count_matches_paper_table3() -> None:
    assert len(REFERENCE) == 9
    shorts = [c.short for c in REFERENCE]
    assert shorts == ["C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "R4"]


def test_third_party_counts_match_csv() -> None:
    expected_tp: dict[str, int] = {
        "C1": 0,
        "C2": 2,
        "C3": 2,
        "C4": 5,
        "C5": 3,
        "R1": 0,
        "R2": 1,
        "R3": 0,
        "R4": 0,
    }
    for cfg in REFERENCE:
        assert cfg.third_party_count == expected_tp[cfg.short]


def test_tool_counts_match_csv() -> None:
    expected_n: dict[str, int] = {
        "C1": 1,
        "C2": 3,
        "C3": 3,
        "C4": 6,
        "C5": 4,
        "R1": 1,
        "R2": 1,
        "R3": 2,
        "R4": 4,
    }
    for cfg in REFERENCE:
        assert len(cfg.tools) == expected_n[cfg.short]
