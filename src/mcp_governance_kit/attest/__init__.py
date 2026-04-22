"""Capability-State Attestation — the primitive defined in SPEC.md.

Exports the pydantic models of :mod:`attest.schema` and, once the
downstream modules land, the full attestation pipeline
(:func:`collect`, :func:`resolve`, :func:`classify`, :func:`sign`,
:func:`verify`).
"""

from __future__ import annotations

from mcp_governance_kit.attest.build import build_attestation
from mcp_governance_kit.attest.classify import Classification, ServerProfile, classify_server
from mcp_governance_kit.attest.collect import CollectedConfig, RawServer, collect
from mcp_governance_kit.attest.schema import (
    SPEC_VERSION,
    Attestation,
    ConfigSource,
    Host,
    HostKind,
    ServerRecord,
    Signature,
    SignatureKind,
    TcsBlock,
    ToolRecord,
    Transport,
)
from mcp_governance_kit.attest.sign import (
    SigstoreUnavailable,
    SigstoreUnavailableError,
    VerificationResult,
    sign_attestation,
    verify_attestation,
)

__all__ = [
    "SPEC_VERSION",
    "Attestation",
    "Classification",
    "CollectedConfig",
    "ConfigSource",
    "Host",
    "HostKind",
    "RawServer",
    "ServerProfile",
    "ServerRecord",
    "Signature",
    "SignatureKind",
    "SigstoreUnavailable",
    "SigstoreUnavailableError",
    "TcsBlock",
    "ToolRecord",
    "Transport",
    "VerificationResult",
    "build_attestation",
    "classify_server",
    "collect",
    "sign_attestation",
    "verify_attestation",
]
