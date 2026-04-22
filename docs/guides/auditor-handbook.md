# Auditor handbook

This page is written for the auditor who has never seen an MCP
attestation before. It tells you: what a conformant attestation looks
like, how to read it, and which clauses of ISO 42001 / NIST AI 600-1 /
EU AI Act each field addresses.

## What you should receive

The deployer should hand you, for each covered host:

1. A **Capability-State Attestation** JSON file, signed via sigstore
   keyless. Schema: `attestation-v0.schema.json`. Spec: `SPEC.md`.
2. The **policy** YAML that was active when the attestation was
   produced. It specifies thresholds and allow-lists.
3. The **policy report** (JSON) produced by `mcp-gov check`. Lists one
   result per breakpoint with severity `pass | info | warn | block`.
4. The **framework mapping** for your target framework (ISO 42001,
   NIST AI 600-1, or EU AI Act). The deployer can emit it with
   `mcp-gov mappings show iso42001`.

## How to verify the attestation

```bash
mcp-gov verify attestation.json \
  --expected-identity user@example.com \
  --expected-issuer https://accounts.google.com
```

The tool:

- validates the JSON against the schema,
- recomputes the TCS from the `tools` array,
- verifies the sigstore bundle against the transparency log and the
  expected identity/issuer.

Any mismatch causes a non-zero exit code.

## Clause mapping

Each breakpoint is mapped to specific clauses. See the
`mcp_governance_kit.mappings` bundle for the authoritative source.

- **ISO/IEC 42001:2023 Annex A** — B1 → A.6.2.5 and A.6.2.6; B2 → A.10.2
  and A.10.3; B4 → A.4.5 and A.9.3; B5 → A.6.2.6 and A.9.4; B6 → A.6.2.4
  and A.6.2.8.
- **NIST AI 600-1** — B1 → GOVERN-1.4-004 and MANAGE-2.4-002; B2 →
  GOVERN-6.1-001 and MAP-4.1-003; B4 → MANAGE-1.2-004 and MANAGE-2.2-001;
  B5 → MEASURE-2.8-001 and MANAGE-2.3-002; B6 → MAP-3.1-002 and
  MANAGE-4.2-001.
- **EU AI Act** — B1 → Art. 55(1)(b); B2 → Art. 25 and 53(1)(b); B4 →
  Art. 14 and 15(4); B5 → Art. 12 and 55(1)(c); B6 → Art. 51 and 55(1)(a).

## What the paper says you will not find

The paper argues that **no published framework text** currently
operationalises a runtime capability-state primitive. The attestation
is that primitive. Treat clause mappings above as the adjacent text you
can cite; treat the attestation itself as the evidence artefact.
