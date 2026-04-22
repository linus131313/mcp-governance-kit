"""B3 — data loss prevention.

Flags tool-graph compositions where data can move from local disk to a
network-reaching write tool without crossing a DLP egress point. The
simplest proxy: any tool graph that contains both a local-read/write
tool and a network-write tool is a potential exfil path.
"""

from __future__ import annotations

from mcp_governance_kit.attest.schema import Attestation
from mcp_governance_kit.breakpoints.base import CheckResult, Severity
from mcp_governance_kit.tcs.models import Action, Reach


def b3_dlp(attestation: Attestation, *, allow_exfil_paths: bool = False) -> CheckResult:
    """Detect potential data-exfiltration paths in the tool graph."""
    local_access = [
        t
        for t in attestation.tools
        if t.reach is Reach.LOCAL and t.action in (Action.READ, Action.WRITE, Action.EXECUTE)
    ]
    net_write = [
        t
        for t in attestation.tools
        if t.reach is Reach.NETWORK and t.action in (Action.WRITE, Action.EXECUTE)
    ]

    if not (local_access and net_write):
        return CheckResult(
            check_id="B3",
            title="Data loss prevention",
            severity=Severity.PASS,
            summary="No local-to-network exfil path in tool graph.",
        )

    paths = [
        f"{lo.server.identity} -> {no.server.identity}" for lo in local_access for no in net_write
    ]
    sev = Severity.INFO if allow_exfil_paths else Severity.WARN
    return CheckResult(
        check_id="B3",
        title="Data loss prevention",
        severity=sev,
        summary=(
            f"{len(local_access)} local-access + {len(net_write)} network-write tool(s) "
            f"= {len(paths)} potential exfil path(s)."
        ),
        details=paths[:20],
        evidence={
            "local_access_count": len(local_access),
            "net_write_count": len(net_write),
            "path_count": len(paths),
        },
    )
