"""B2 — third-party risk.

Enumerates the third-party servers bound to the host and cross-checks
them against an allow-list. Servers that are not on the list are WARN
(INFO if an explicit exception tag is supplied); exceeding a configured
max count is BLOCK.
"""

from __future__ import annotations

from collections.abc import Iterable

from mcp_governance_kit.attest.schema import Attestation
from mcp_governance_kit.breakpoints.base import CheckResult, Severity


def b2_thirdparty(
    attestation: Attestation,
    *,
    allowlist: Iterable[str] = (),
    max_third_party: int | None = None,
) -> CheckResult:
    """Check third-party server exposure."""
    allowed = set(allowlist)
    third_party = [t for t in attestation.tools if t.server.third_party]
    unapproved = sorted({t.server.identity for t in third_party} - allowed)

    if max_third_party is not None and len(third_party) > max_third_party:
        return CheckResult(
            check_id="B2",
            title="Third-party risk",
            severity=Severity.BLOCK,
            summary=(
                f"{len(third_party)} third-party server(s), "
                f"exceeds policy maximum of {max_third_party}."
            ),
            details=[t.server.identity for t in third_party],
            evidence={"third_party_count": len(third_party)},
        )

    if unapproved:
        return CheckResult(
            check_id="B2",
            title="Third-party risk",
            severity=Severity.WARN,
            summary=f"{len(unapproved)} third-party server(s) not on allow-list.",
            details=unapproved,
            evidence={
                "unapproved_count": len(unapproved),
                "third_party_count": len(third_party),
            },
        )

    return CheckResult(
        check_id="B2",
        title="Third-party risk",
        severity=Severity.PASS,
        summary=f"All {len(third_party)} third-party server(s) are on the allow-list.",
        evidence={"third_party_count": len(third_party)},
    )
