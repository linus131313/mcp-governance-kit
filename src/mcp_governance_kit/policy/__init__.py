"""Policy engine: evaluate an attestation against a YAML policy document."""

from __future__ import annotations

from mcp_governance_kit.policy.engine import Policy, PolicyReport, evaluate

__all__ = ["Policy", "PolicyReport", "evaluate"]
