# Capability-State Attestation

An **attestation** is a reproducible, signable snapshot of a host's
runtime capability graph: what tools are bound, with what reach and
action-level privilege, through what trust path, together with a TCS
score, at a single point in time.

The full specification lives in [`SPEC.md`](../spec.md). The pydantic
model and the JSON Schema shipped in the wheel are the authoritative
artefacts; the spec document tracks them.

## Lifecycle

1. **Collect** — parse the MCP config file (Claude Desktop, Claude
   Code, Cursor). The source path and SHA-256 are recorded.
2. **Classify** — each server's identity, reach, action, and
   third-party flag are derived from a deterministic classifier with a
   published catalogue and optional overrides.
3. **Score** — TCS is computed with the paper's default weights; the
   exact weights used are recorded in the attestation.
4. **Sign** — sigstore keyless produces a Rekor-logged signature bound
   to a GitHub OIDC identity or an email OAuth identity.
5. **Verify** — any party can re-parse the JSON, recompute TCS, and
   check the signature against the transparency log.

## Fields

See the [SPEC](../spec.md) for the full field list. The high-level
shape is:

- `host`, `config_source`
- `tools[]` with per-tool `server`, `reach`, `action`, `resolved`
- `tcs.value`, `tcs.weights`, `tcs.third_party_count`
- `policy_refs[]`, `signature`
