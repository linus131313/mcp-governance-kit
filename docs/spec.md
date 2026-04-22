# Capability-State Attestation — SPEC v0

The canonical SPEC document is
[`SPEC.md`](https://github.com/linus131313/mcp-governance-kit/blob/main/SPEC.md)
in the repository root. It defines the attestation format in detail
and is the version-controlled source of truth for:

- document structure and required fields,
- how to produce an attestation (MCP handshake, classification, TCS),
- how to verify an attestation (schema, signature, TCS recompute),
- the change-management diff operation (Breakpoint B1),
- versioning rules (`spec_version`).

The authoritative JSON Schema for v0 is shipped in the wheel at
`src/mcp_governance_kit/attest/schemas/attestation-v0.schema.json` and
is regenerated from the pydantic model in `src/mcp_governance_kit/attest/schema.py`.
CI verifies that the on-disk schema matches the model on every push.
