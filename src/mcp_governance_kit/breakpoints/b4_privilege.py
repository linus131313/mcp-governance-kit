"""B4 — privileged access.

Two sub-checks:

1. TCS threshold. If the attestation's TCS exceeds the configured
   threshold, the check escalates to WARN or BLOCK.
2. Execute capability. Any tool with ``action=execute`` is flagged;
   network+execute combinations are the strictest and go to BLOCK when
   ``require_approval_for_execute`` is enabled.
"""

from __future__ import annotations

from mcp_governance_kit.attest.schema import Attestation
from mcp_governance_kit.breakpoints.base import CheckResult, Severity
from mcp_governance_kit.tcs.models import Action, Reach


def b4_privilege(
    attestation: Attestation,
    *,
    max_tcs: float | None = None,
    warn_tcs: float | None = None,
    require_approval_for_execute: bool = False,
    execute_approved: bool = False,
) -> CheckResult:
    """Evaluate privileged-access exposure."""
    tcs_value = attestation.tcs.value
    execute_tools = [t for t in attestation.tools if t.action is Action.EXECUTE]
    net_execute_tools = [t for t in execute_tools if t.reach is Reach.NETWORK]

    details: list[str] = []
    evidence: dict[str, str | int | float | bool] = {
        "tcs": tcs_value,
        "execute_tools": len(execute_tools),
        "network_execute_tools": len(net_execute_tools),
    }

    if max_tcs is not None and tcs_value > max_tcs:
        details.extend(f"execute: {t.server.identity}" for t in execute_tools)
        return CheckResult(
            check_id="B4",
            title="Privileged access",
            severity=Severity.BLOCK,
            summary=f"TCS {tcs_value} exceeds policy maximum {max_tcs}.",
            details=details,
            evidence=evidence,
        )

    if require_approval_for_execute and net_execute_tools and not execute_approved:
        return CheckResult(
            check_id="B4",
            title="Privileged access",
            severity=Severity.BLOCK,
            summary=(
                f"{len(net_execute_tools)} network-reaching execute tool(s) require approval."
            ),
            details=[t.server.identity for t in net_execute_tools],
            evidence=evidence,
        )

    if warn_tcs is not None and tcs_value > warn_tcs:
        return CheckResult(
            check_id="B4",
            title="Privileged access",
            severity=Severity.WARN,
            summary=f"TCS {tcs_value} exceeds advisory threshold {warn_tcs}.",
            evidence=evidence,
        )

    if execute_tools:
        return CheckResult(
            check_id="B4",
            title="Privileged access",
            severity=Severity.INFO,
            summary=f"{len(execute_tools)} execute-capable tool(s) bound; within thresholds.",
            details=[t.server.identity for t in execute_tools],
            evidence=evidence,
        )

    return CheckResult(
        check_id="B4",
        title="Privileged access",
        severity=Severity.PASS,
        summary=f"No execute-capable tools; TCS {tcs_value} within thresholds.",
        evidence=evidence,
    )
