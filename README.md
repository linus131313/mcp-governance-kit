# mcp-governance-kit

> Runtime capability-state attestation for Model Context Protocol agents.
> Companion implementation to [*The MCP Governance Gap* (Teklenburg, 2026)](paper/governance-speed-gap.pdf).

[![CI](https://github.com/linus131313/mcp-governance-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/linus131313/mcp-governance-kit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mcp-governance-kit.svg)](https://pypi.org/project/mcp-governance-kit/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-governance-kit.svg)](https://pypi.org/project/mcp-governance-kit/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## Why this exists

Every enterprise governance framework in use today — ISO/IEC 42001:2023, NIST AI RMF (AI 600-1), EU AI Act — was drafted before the Model Context Protocol existed. None of them names dynamic tool binding as a governance object. The companion paper quantifies the resulting gap across 97,980 MCP-server repositories, ten publicly disclosed incidents, and six control breakpoints, and argues that closing the gap requires a new primitive that no published framework yet defines:

> **Runtime capability-state attestation** — a reproducible, signable snapshot of what tools an agent can reach, with what action-level privilege, through what trust path, that an auditor can test against.

This repository is a reference implementation of that primitive.

## What you get

- **`mcp-gov score`** — compute the Tool Graph Capability Score (TCS) for any MCP configuration. Reproduces Table 3 of the paper exactly.
- **`mcp-gov attest`** — collect, classify, and sign a capability-state attestation from your live MCP configs (Claude Desktop, Claude Code, Cursor).
- **`mcp-gov check`** — evaluate an attestation against the six control breakpoints (B1–B6) from the paper and policy YAML.
- **`mcp-gov verify`** — verify sigstore signatures and diff two attestations to surface change-management events.
- **Framework mappings** — each check links to the specific ISO 42001 Annex A, NIST AI 600-1, and EU AI Act clauses it addresses, so an auditor can cite the evidence.
- **Integrations** — GitHub Action, pre-commit hook, and Claude Code `PreToolUse` hook.

## Quickstart

```bash
pip install mcp-governance-kit

# reproduce Table 3 of the paper
mcp-gov score examples/c3-developer.mcp.json
# → TCS = 13.5

# attest your actual Claude Code configuration
mcp-gov attest ~/.claude/settings.json --sign --out attestation.json

# run the six breakpoint checks
mcp-gov check attestation.json --policy policies/default.yaml
```

## Specification

The attestation format is versioned and documented as a public spec:
see [`SPEC.md`](SPEC.md) — *Capability-State Attestation v0*.

## Paper

The companion paper lives in [`paper/governance-speed-gap.pdf`](paper/governance-speed-gap.pdf).
Cite via [`paper/CITATION.cff`](paper/CITATION.cff).

## License

- Code: [Apache-2.0](LICENSE)
- Paper PDF and documentation: [CC BY 4.0](LICENSE-docs)

## Status

Alpha. The TCS scorer and attestation collector are stable; signing, the full
breakpoint suite, and the framework mappings are in progress toward a v0.1.0
release. See [`CHANGELOG.md`](CHANGELOG.md).
