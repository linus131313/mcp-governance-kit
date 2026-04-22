"""Glue the collector, classifier, and TCS scorer into a single
``build_attestation()`` entry point.

This is the primary public surface of the attestation pipeline. The CLI
``mcp-gov attest`` is a thin wrapper around it.
"""

from __future__ import annotations

from pathlib import Path

from mcp_governance_kit.attest.classify import Classification, classify_server
from mcp_governance_kit.attest.collect import CollectedConfig, collect
from mcp_governance_kit.attest.schema import (
    Attestation,
    Host,
    HostKind,
    TcsBlock,
    ToolRecord,
)
from mcp_governance_kit.tcs.models import Config, Tool
from mcp_governance_kit.tcs.score import tcs
from mcp_governance_kit.tcs.weights import DEFAULT_WEIGHTS, Weights


def build_attestation(
    config_path: Path,
    *,
    host_id: str,
    host_kind: HostKind | None = None,
    host_version: str | None = None,
    weights: Weights | None = None,
    overrides: Classification | None = None,
    policy_refs: list[str] | None = None,
) -> Attestation:
    """Build a full (unsigned) :class:`Attestation` from a config file."""
    collected: CollectedConfig = collect(config_path, host_kind=host_kind)
    tool_records: list[ToolRecord] = [classify_server(s, overrides) for s in collected.servers]

    used_weights = weights or DEFAULT_WEIGHTS
    tcs_config = Config(
        label=f"attestation for {host_id}",
        short="ATT",
        tools=[
            Tool(
                name=t.name,
                reach=t.reach,
                action=t.action,
                third_party=t.server.third_party,
            )
            for t in tool_records
        ],
    )

    return Attestation(
        host=Host(id=host_id, kind=collected.host_kind, version=host_version),
        config_source=collected.source,
        tools=tool_records,
        tcs=TcsBlock(
            value=tcs(tcs_config, used_weights),
            weights=used_weights.model_dump(),
            third_party_count=tcs_config.third_party_count,
        ),
        policy_refs=policy_refs or [],
    )
