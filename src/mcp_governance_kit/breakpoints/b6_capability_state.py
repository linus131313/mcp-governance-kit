"""B6 — AI-specific capability state.

Per the paper's diagnosis: AI governance frameworks review models at
deployment, but the capability graph can change without a model update.
B6 flags the case where the tool graph changed without the host version
changing (i.e. the model/host appears identical, but the capability
surface shifted). This is the gap ISO 42001 A.6 / NIST AI 600-1 do not
currently address.
"""

from __future__ import annotations

from mcp_governance_kit.attest.schema import Attestation, ToolRecord
from mcp_governance_kit.breakpoints.base import CheckResult, Severity


def _graph_fingerprint(tools: list[ToolRecord]) -> frozenset[tuple[str, str, str, str, bool]]:
    return frozenset(
        (
            t.name,
            t.server.identity,
            t.reach.value,
            t.action.value,
            t.server.third_party,
        )
        for t in tools
    )


def b6_capability_state(
    previous: Attestation | None,
    current: Attestation,
) -> CheckResult:
    """Detect silent capability-surface changes under a stable host version."""
    if previous is None:
        return CheckResult(
            check_id="B6",
            title="AI-specific capability state",
            severity=Severity.INFO,
            summary="First-time attestation; no prior state to compare.",
        )

    host_stable = (
        previous.host.kind == current.host.kind and previous.host.version == current.host.version
    )
    graph_changed = _graph_fingerprint(previous.tools) != _graph_fingerprint(current.tools)

    if host_stable and graph_changed:
        return CheckResult(
            check_id="B6",
            title="AI-specific capability state",
            severity=Severity.WARN,
            summary=("Tool graph changed while host version remained stable — classic B6 gap."),
            evidence={
                "host_kind": current.host.kind.value,
                "host_version": current.host.version or "",
                "previous_tcs": previous.tcs.value,
                "current_tcs": current.tcs.value,
            },
        )

    if graph_changed:
        return CheckResult(
            check_id="B6",
            title="AI-specific capability state",
            severity=Severity.INFO,
            summary="Graph changed together with host version; expected re-review event.",
        )

    return CheckResult(
        check_id="B6",
        title="AI-specific capability state",
        severity=Severity.PASS,
        summary="Capability graph stable under stable host version.",
    )
