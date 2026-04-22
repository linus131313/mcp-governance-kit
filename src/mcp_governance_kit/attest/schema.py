"""Pydantic models for the Capability-State Attestation (SPEC.md, v0).

The model is the single source of truth. The JSON Schema file at
``src/mcp_governance_kit/attest/schemas/attestation-v0.schema.json`` is
an exported artefact produced by :func:`export_json_schema` and pinned
in tests so schema drift is never silent.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from mcp_governance_kit.tcs.models import Action, Reach

SPEC_VERSION = "0"
"""Current attestation spec version. See SPEC.md."""


class HostKind(StrEnum):
    """Known MCP host kinds; ``custom`` is the escape hatch."""

    CLAUDE_DESKTOP = "claude-desktop"
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    CUSTOM = "custom"


class Transport(StrEnum):
    """MCP wire transports as of the 2025-11-25 spec."""

    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable-http"


class SignatureKind(StrEnum):
    """How the attestation is signed."""

    SIGSTORE_KEYLESS = "sigstore-keyless"
    UNSIGNED = "unsigned"


class Host(BaseModel):
    """The MCP host the attestation describes."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, description="Stable host identifier (hostname, agent name).")
    kind: HostKind
    version: str | None = None


class ConfigSource(BaseModel):
    """The config file that was parsed to produce the attestation."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ServerRecord(BaseModel):
    """An MCP server bound to the host."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    transport: Transport
    identity: str = Field(
        min_length=1,
        description="Package name, URL, or binary path that uniquely identifies the server.",
    )
    version: str | None = None
    third_party: bool


class ToolRecord(BaseModel):
    """A tool advertised by a server."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    server: ServerRecord
    reach: Reach
    action: Action
    description: str | None = None
    resolved: bool = Field(
        description=(
            "True if the tool metadata came from a live MCP handshake; "
            "False if it was derived from a static manifest or the config alone."
        )
    )


class TcsBlock(BaseModel):
    """The computed TCS value together with the exact weights used."""

    model_config = ConfigDict(extra="forbid")

    value: float = Field(ge=0)
    weights: dict[str, float]
    third_party_count: int = Field(ge=0)


class Signature(BaseModel):
    """Signature envelope. ``bundle`` is populated for sigstore-keyless."""

    model_config = ConfigDict(extra="forbid")

    kind: SignatureKind
    bundle: str | None = Field(
        default=None,
        description="Base64-encoded sigstore bundle when kind=sigstore-keyless.",
    )


class Attestation(BaseModel):
    """A Capability-State Attestation v0 document."""

    model_config = ConfigDict(extra="forbid")

    spec_version: str = Field(default=SPEC_VERSION)
    attestation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        pattern=(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
            r"[0-9a-f]{4}-[0-9a-f]{12}$"
        ),
    )
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    host: Host
    config_source: ConfigSource
    tools: list[ToolRecord]
    tcs: TcsBlock
    policy_refs: list[str] = Field(default_factory=list)
    signature: Signature = Field(default_factory=lambda: Signature(kind=SignatureKind.UNSIGNED))


def export_json_schema() -> dict[str, Any]:
    """Generate the JSON Schema for :class:`Attestation`.

    This is the authoritative schema cited in ``SPEC.md``. The on-disk
    copy at ``attest/schemas/attestation-v0.schema.json`` is regenerated
    from this function and the regeneration is verified in tests.
    """
    schema = Attestation.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = (
        "https://github.com/linus131313/mcp-governance-kit/"
        "blob/main/src/mcp_governance_kit/attest/schemas/attestation-v0.schema.json"
    )
    schema["title"] = "Capability-State Attestation v0"
    return schema


_SCHEMA_PATH = Path(__file__).parent / "schemas" / "attestation-v0.schema.json"


def load_schema_from_disk() -> dict[str, Any]:
    """Return the exported JSON Schema shipped in the wheel."""
    result: dict[str, Any] = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return result
