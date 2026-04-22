"""Capability-State Attestation — the primitive defined in SPEC.md.

Exports the pydantic models of :mod:`attest.schema` and, once the
downstream modules land, the full attestation pipeline
(:func:`collect`, :func:`resolve`, :func:`classify`, :func:`sign`,
:func:`verify`).
"""

from __future__ import annotations

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

__all__ = [
    "SPEC_VERSION",
    "Attestation",
    "ConfigSource",
    "Host",
    "HostKind",
    "ServerRecord",
    "Signature",
    "SignatureKind",
    "TcsBlock",
    "ToolRecord",
    "Transport",
]
