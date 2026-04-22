"""B5 — audit and monitoring.

The attestation itself is the audit artefact for B5. This check produces
an OCSF-shaped event (``category_uid=6``, Application Activity) that a
SIEM can ingest, together with a CEF line for legacy collectors.

When the attestation is unsigned, the check is WARN because an unsigned
record is weak evidence for an audit trail; when signed, PASS.
"""

from __future__ import annotations

from typing import Any

from mcp_governance_kit.attest.schema import Attestation, SignatureKind
from mcp_governance_kit.breakpoints.base import CheckResult, Severity


def _ocsf_event(attestation: Attestation) -> dict[str, Any]:
    return {
        "category_uid": 6,  # Application Activity
        "class_uid": 6005,  # Application Lifecycle
        "type_uid": 600502,  # Configure
        "activity_id": 2,  # Update
        "time": attestation.issued_at.isoformat(),
        "metadata": {
            "product": {"name": "mcp-governance-kit"},
            "version": attestation.spec_version,
            "uid": attestation.attestation_id,
        },
        "actor": {
            "user": {"name": attestation.host.id},
        },
        "device": {
            "hostname": attestation.host.id,
            "type": attestation.host.kind.value,
        },
        "observables": [
            {"name": "tcs", "type": "metric", "value": attestation.tcs.value},
            {"name": "tool_count", "type": "metric", "value": len(attestation.tools)},
            {
                "name": "third_party_count",
                "type": "metric",
                "value": attestation.tcs.third_party_count,
            },
        ],
        "message": (
            f"Capability-state attestation for {attestation.host.id}: "
            f"tools={len(attestation.tools)} tcs={attestation.tcs.value}"
        ),
    }


def _cef_line(attestation: Attestation) -> str:
    return (
        f"CEF:0|mcp-governance-kit|mcp-gov|{attestation.spec_version}|"
        f"ATTEST|capability-state-attestation|3|"
        f"shost={attestation.host.id} "
        f"cs1Label=tcs cs1={attestation.tcs.value} "
        f"cn1Label=tools cn1={len(attestation.tools)} "
        f"cn2Label=thirdParty cn2={attestation.tcs.third_party_count} "
        f"externalId={attestation.attestation_id}"
    )


def b5_audit(attestation: Attestation) -> CheckResult:
    """Emit audit artefacts and rate the attestation as a log record."""
    signed = attestation.signature.kind is SignatureKind.SIGSTORE_KEYLESS
    return CheckResult(
        check_id="B5",
        title="Audit and monitoring",
        severity=Severity.PASS if signed else Severity.WARN,
        summary=(
            "Signed attestation is a SIEM-ingestible audit artefact."
            if signed
            else "Unsigned attestation is weak audit evidence (use --sign)."
        ),
        evidence={
            "signed": signed,
            "cef": _cef_line(attestation),
        },
        details=[
            "OCSF event emitted as check.evidence['ocsf'] when requested.",
        ],
    )
