"""Sensitivity analysis over the 48-point reweighting grid (§5.3)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from mcp_governance_kit.tcs.models import Config
from mcp_governance_kit.tcs.score import tcs
from mcp_governance_kit.tcs.weights import DEFAULT_WEIGHTS, Weights, reweighting_grid


class SensitivityReport(BaseModel):
    """Structured result of :func:`sensitivity_analysis`."""

    model_config = ConfigDict(extra="forbid")

    settings_count: int = Field(ge=1)
    default_ranking: list[str]
    exact_match_count: int = Field(ge=0)
    invariants: dict[str, int]
    """Map from invariant name ("C4_gt_R4", …) to the number of grid points
    at which it holds."""

    @property
    def exact_match_fraction(self) -> float:
        return self.exact_match_count / self.settings_count


def _ranking(configs: list[Config], weights: Weights) -> list[str]:
    return [c.short for c in sorted(configs, key=lambda c: tcs(c, weights), reverse=True)]


def sensitivity_analysis(
    configs: list[Config],
    *,
    grid: list[Weights] | None = None,
) -> SensitivityReport:
    """Run the 48-point sensitivity grid over ``configs``.

    Reproduces the three headline invariants of §5.3:
    ``C4 > R4``, ``C3 > R3``, ``C2 > R3``.

    Parameters
    ----------
    configs:
        The configurations to rank. Typically ``REFERENCE``.
    grid:
        Optional custom weight grid. Defaults to :func:`reweighting_grid`.
    """
    points = grid or reweighting_grid()
    default_ranking = _ranking(configs, DEFAULT_WEIGHTS)

    exact_match_count = 0
    invariants: dict[str, int] = {}
    pairs = [("C4", "R4"), ("C3", "R3"), ("C2", "R3")]
    for a, b in pairs:
        invariants[f"{a}_gt_{b}"] = 0

    for weights in points:
        ranking = _ranking(configs, weights)
        if ranking == default_ranking:
            exact_match_count += 1
        for a, b in pairs:
            if a in ranking and b in ranking and ranking.index(a) < ranking.index(b):
                invariants[f"{a}_gt_{b}"] += 1

    return SensitivityReport(
        settings_count=len(points),
        default_ranking=default_ranking,
        exact_match_count=exact_match_count,
        invariants=invariants,
    )
