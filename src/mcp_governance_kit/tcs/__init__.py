"""Tool Graph Capability Score (TCS).

Reproduces the scoring algorithm of §5.3 of the companion paper
"The MCP Governance Gap" (Teklenburg, 2026).

TCS is a reproducibility-first comparability metric, not a safety metric.
It lets a governance programme place an agent configuration on the same
axis as a traditional approved application.
"""

from __future__ import annotations

from mcp_governance_kit.tcs.models import Action, Config, Reach, Tool
from mcp_governance_kit.tcs.reference import COMPARATORS, CONFIGURATIONS, REFERENCE
from mcp_governance_kit.tcs.score import tcs
from mcp_governance_kit.tcs.sensitivity import SensitivityReport, sensitivity_analysis
from mcp_governance_kit.tcs.weights import DEFAULT_WEIGHTS, Weights, reweighting_grid

__all__ = [
    "COMPARATORS",
    "CONFIGURATIONS",
    "DEFAULT_WEIGHTS",
    "REFERENCE",
    "Action",
    "Config",
    "Reach",
    "SensitivityReport",
    "Tool",
    "Weights",
    "reweighting_grid",
    "sensitivity_analysis",
    "tcs",
]
