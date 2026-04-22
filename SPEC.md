# Capability-State Attestation, Version 0

**Status:** Draft v0.
**Companion paper:** Teklenburg, L. (2026). *The MCP Governance Gap: Empirical Evidence on Dynamic Tool Binding in Enterprise AI.* See [`paper/governance-speed-gap.pdf`](paper/governance-speed-gap.pdf).

## 1. Purpose

This specification defines a reproducible, signable snapshot of the
runtime capability graph of a Model-Context-Protocol (MCP) host. The
snapshot is the auditable object the companion paper argues is
missing from every AI-specific governance framework in applicable form
as of April 2026.

A conformant implementation of this specification produces an
*attestation*: a JSON document that

1. enumerates the tools bound to a host at a single point in time,
2. classifies each tool's reach and action-level privilege,
3. records a scalar capability score (TCS) over the graph, and
4. is cryptographically signed so that the document's integrity and
   issuer are verifiable without trusting the host.

## 2. Terminology

- **Host.** The process that runs an MCP client — a coding assistant,
  a chat client, or a custom agent.
- **Server.** An MCP server, reachable via `stdio`, `sse`, or
  `streamable-http` transport, that advertises one or more tools.
- **Tool.** A named capability exposed by a server, invokable by the
  host's model via JSON-RPC `tools/call`.
- **Tool graph.** The set of tools bound to a host at a given moment.
- **Third-party server.** A server maintained by any principal other
  than the host vendor. The classifier in
  `src/mcp_governance_kit/attest/classify.py` is authoritative.
- **Issuer.** The identity that signs the attestation. In CI, the
  GitHub OIDC identity of the runner; locally, a sigstore OIDC email
  identity.

## 3. Document structure

Attestations are UTF-8 JSON. The authoritative schema is
`src/mcp_governance_kit/attest/schemas/attestation-v0.schema.json`.
The normative fields are:

```json
{
  "spec_version": "0",
  "attestation_id": "<uuid4>",
  "issued_at": "<RFC 3339 UTC timestamp>",
  "host": {
    "id": "<stable host identifier, e.g. hostname or agent name>",
    "kind": "claude-desktop | claude-code | cursor | custom",
    "version": "<host version string, optional>"
  },
  "config_source": {
    "path": "<absolute or repo-relative path that was parsed>",
    "sha256": "<hex sha256 of the config file contents>"
  },
  "tools": [
    {
      "name": "<tool name>",
      "server": {
        "name": "<server name as declared in the config>",
        "transport": "stdio | sse | streamable-http",
        "identity": "<package name, url, or binary path>",
        "version": "<version string or null>",
        "third_party": true
      },
      "reach": "local | network",
      "action": "read | write | execute",
      "description": "<MCP tool description, if resolved>",
      "resolved": true
    }
  ],
  "tcs": {
    "value": 13.5,
    "weights": {
      "w_local": 1.0,
      "w_network": 2.0,
      "w_read": 1.0,
      "w_write": 2.0,
      "w_execute": 3.0,
      "t_coef": 0.25
    },
    "third_party_count": 2
  },
  "policy_refs": [
    "policies/developer.yaml#v1"
  ],
  "signature": {
    "kind": "sigstore-keyless | unsigned",
    "bundle": "<sigstore bundle JSON, base64, when kind=sigstore-keyless>"
  }
}
```

All fields are REQUIRED unless explicitly marked optional in the JSON
Schema. `signature.kind = "unsigned"` is permitted for local development
but MUST NOT be accepted by a production verifier.

## 4. Producing an attestation

A conformant producer MUST:

1. Parse the host's MCP configuration from a single, identified source
   file. Record the file's absolute path and SHA-256 in
   `config_source`.
2. Enumerate every server and tool. Where the server is reachable,
   perform an MCP `initialize` + `tools/list` handshake and mark
   `tools[].resolved = true`. Where the server is not reachable,
   `tools/list` MAY be derived from a declared manifest and
   `resolved = false`.
3. Classify each tool's `reach` and `action` using the deterministic
   heuristic in `src/mcp_governance_kit/attest/classify.py`, or a
   documented override recorded elsewhere in the repository.
4. Compute TCS using the formula of the companion paper §5.3 and
   record the exact weights used under `tcs.weights`.
5. Sign the document. Production issuers MUST use sigstore keyless
   signing; the bundle MUST include the transparency-log entry
   (Rekor) so any verifier can recompute inclusion.

## 5. Verifying an attestation

A conformant verifier MUST:

1. Reject any document whose `spec_version` it does not understand.
2. Validate the document against the JSON Schema.
3. Verify the signature bundle against the declared issuer identity
   and the Rekor transparency log.
4. Recompute TCS from the `tools` array using the recorded `weights`
   and compare to `tcs.value`. Mismatches MUST cause rejection.
5. Recompute `config_source.sha256` only if the config file is still
   available; mismatches SHOULD be surfaced as a diagnostic but do
   not invalidate an archived attestation.

## 6. Change-management diff (Breakpoint B1)

Two attestations of the same host form a *change set*. A conformant
diff operation returns the ordered lists:

- tools added (`name` + `server.identity` + `server.version`),
- tools removed,
- tools whose classification changed (`reach`, `action`, or
  `third_party`),
- delta TCS.

The change set is the evidence artefact for ISO/IEC 27001 A.8.32,
COBIT BAI06, and ISO/IEC 42001 Annex A.6.2.5 when audited against an
MCP-native host.

## 7. Relationship to frameworks

The attestation primitive is intentionally framework-agnostic. The
mapping from attestation fields to specific clauses of ISO 42001,
NIST AI 600-1, and the EU AI Act is maintained in
`src/mcp_governance_kit/mappings/` as a separate, versioned artefact.

## 8. Versioning

This document specifies version `0`. Backwards-incompatible changes
will increment `spec_version` and ship a new schema file. Producers
SHOULD emit the lowest `spec_version` they support; verifiers SHOULD
accept any `spec_version` ≤ their maximum.
