"""Sensitivity analysis tests — reproduce the §5.3 headline invariants.

From the paper:
    C4 > R4 in 48 of 48 reweightings
    C3 > R3 in 48 of 48
    C2 > R3 in 39 of 48
    exact global ranking preserved in 20 of 48 settings
"""

from __future__ import annotations

from mcp_governance_kit.tcs import REFERENCE, reweighting_grid, sensitivity_analysis


def test_grid_size() -> None:
    assert len(reweighting_grid()) == 48


def test_sensitivity_headline_invariants() -> None:
    report = sensitivity_analysis(REFERENCE)
    assert report.settings_count == 48
    assert report.invariants["C4_gt_R4"] == 48
    assert report.invariants["C3_gt_R3"] == 48
    assert report.invariants["C2_gt_R3"] == 39


def test_exact_ranking_stability() -> None:
    report = sensitivity_analysis(REFERENCE)
    assert report.exact_match_count == 20


def test_default_ranking_places_c4_on_top() -> None:
    report = sensitivity_analysis(REFERENCE)
    assert report.default_ranking[0] == "C4"
    assert report.default_ranking.index("C4") < report.default_ranking.index("R4")
