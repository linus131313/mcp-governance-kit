"""B1 — change management.

Compares two attestations of the same host. Any added, removed, or
reclassified tool is a change that would, under traditional change
management, generate a change record. The check is WARN if any change
is present and the ``changes_approved`` flag is not set; BLOCK if
``require_approval`` is enabled in the policy context and the flag is
not set. PASS otherwise.
"""

from __future__ import annotations

from mcp_governance_kit.attest.schema import Attestation, ToolRecord
from mcp_governance_kit.breakpoints.base import CheckResult, Severity


def _tool_key(t: ToolRecord) -> str:
    return f"{t.name}@{t.server.identity}"


def b1_change(
    previous: Attestation | None,
    current: Attestation,
    *,
    changes_approved: bool = False,
    require_approval: bool = False,
) -> CheckResult:
    """Compare two attestations and surface the change set.

    If ``previous`` is ``None`` the check is considered INFO (first-time
    attestation, no change to compare against).
    """
    if previous is None:
        return CheckResult(
            check_id="B1",
            title="Change management",
            severity=Severity.INFO,
            summary="No prior attestation supplied; change set cannot be computed.",
        )

    prev_by_key = {_tool_key(t): t for t in previous.tools}
    curr_by_key = {_tool_key(t): t for t in current.tools}

    added = sorted(set(curr_by_key) - set(prev_by_key))
    removed = sorted(set(prev_by_key) - set(curr_by_key))
    reclassified: list[str] = []
    for key in set(prev_by_key) & set(curr_by_key):
        p, c = prev_by_key[key], curr_by_key[key]
        if (p.reach, p.action, p.server.third_party) != (c.reach, c.action, c.server.third_party):
            reclassified.append(key)
    reclassified.sort()

    total_changes = len(added) + len(removed) + len(reclassified)
    tcs_delta = current.tcs.value - previous.tcs.value

    if total_changes == 0:
        return CheckResult(
            check_id="B1",
            title="Change management",
            severity=Severity.PASS,
            summary="Tool graph unchanged since previous attestation.",
            evidence={"tcs_delta": tcs_delta},
        )

    details = (
        [f"+ {k}" for k in added] + [f"- {k}" for k in removed] + [f"~ {k}" for k in reclassified]
    )

    if changes_approved:
        sev = Severity.INFO
        msg = f"{total_changes} approved change(s) since previous attestation."
    elif require_approval:
        sev = Severity.BLOCK
        msg = f"{total_changes} unapproved change(s) detected. Policy requires approval for B1."
    else:
        sev = Severity.WARN
        msg = f"{total_changes} change(s) detected without change record."

    return CheckResult(
        check_id="B1",
        title="Change management",
        severity=sev,
        summary=msg,
        details=details,
        evidence={
            "added": len(added),
            "removed": len(removed),
            "reclassified": len(reclassified),
            "tcs_delta": tcs_delta,
        },
    )
