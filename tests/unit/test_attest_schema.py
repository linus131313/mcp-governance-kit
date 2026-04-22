"""Attestation schema tests.

Pins two invariants:

1. Round-trip: a valid attestation serialises and re-parses without
   losing fields.
2. Schema drift: the JSON Schema file shipped in the wheel matches the
   one produced from the pydantic model. Keeps the spec document and
   the code in lockstep.
"""

from __future__ import annotations

import json

import jsonschema
import pytest
from pydantic import ValidationError

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
    export_json_schema,
    load_schema_from_disk,
)
from mcp_governance_kit.tcs.models import Action, Reach


def _example_attestation() -> Attestation:
    return Attestation(
        host=Host(id="dev-laptop-1", kind=HostKind.CLAUDE_CODE, version="1.2.3"),
        config_source=ConfigSource(path="/repo/.mcp.json", sha256="a" * 64),
        tools=[
            ToolRecord(
                name="list_issues",
                server=ServerRecord(
                    name="github",
                    transport=Transport.STDIO,
                    identity="npm:@modelcontextprotocol/server-github",
                    version="0.5.0",
                    third_party=True,
                ),
                reach=Reach.NETWORK,
                action=Action.WRITE,
                description="List GitHub issues for a repo.",
                resolved=True,
            ),
        ],
        tcs=TcsBlock(
            value=6.0,
            weights={"w_network": 2, "w_write": 2, "t_coef": 0.25},
            third_party_count=1,
        ),
        signature=Signature(kind=SignatureKind.UNSIGNED),
    )


def test_round_trip_preserves_fields() -> None:
    src = _example_attestation()
    payload = src.model_dump_json()
    dst = Attestation.model_validate_json(payload)
    assert dst == src


def test_spec_version_pinned() -> None:
    assert SPEC_VERSION == "0"
    assert _example_attestation().spec_version == "0"


def test_disk_schema_matches_model() -> None:
    on_disk = load_schema_from_disk()
    regenerated = export_json_schema()
    assert on_disk == regenerated, (
        "JSON Schema on disk drifted from the model. Run scripts/export_schema.py to regenerate."
    )


def test_example_validates_against_json_schema() -> None:
    schema = load_schema_from_disk()
    data = json.loads(_example_attestation().model_dump_json())
    jsonschema.validate(data, schema)


def test_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Attestation.model_validate(
            {**json.loads(_example_attestation().model_dump_json()), "foo": 1}
        )


def test_rejects_bad_sha256() -> None:
    with pytest.raises(ValidationError):
        ConfigSource(path="x", sha256="not-a-sha")
