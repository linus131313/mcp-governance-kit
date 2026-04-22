# mcp-governance-kit

Runtime capability-state attestation for Model Context Protocol agents.

Companion implementation to [*The MCP Governance Gap*](paper.md)
(Teklenburg, 2026). The paper identifies a missing governance primitive:

> a reproducible, signable snapshot of what tools an agent can reach,
> with what action-level privilege, through what trust path, that an
> auditor can test against.

This kit implements that primitive. It ships:

- a Tool Graph Capability Score (TCS) scorer that reproduces Table 3 of
  the paper exactly;
- a JSON-Schema'd, versioned attestation format signable with sigstore;
- six control-breakpoint checks (B1–B6) mapped to ISO 42001, NIST AI
  600-1, and the EU AI Act;
- three adoption paths — GitHub Action, pre-commit hook, Claude Code
  PreToolUse hook.

## Install

```bash
pip install mcp-governance-kit             # core
pip install 'mcp-governance-kit[sign]'     # + sigstore signing
```

## One-minute demo

```bash
mcp-gov attest .mcp.json --host-id $HOSTNAME --out att.json --sign
mcp-gov check att.json --policy policies/default.yaml
```

See [Quickstart](quickstart.md) for a full walk-through.
