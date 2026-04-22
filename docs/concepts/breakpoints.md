# Control Breakpoints B1–B6

The six control families from Table 6 of the paper, each operationalised
as a Python function that returns a structured `CheckResult`.

| Check | Control family | Behaviour |
|-------|----------------|-----------|
| B1 | Change management | Diffs two attestations, flags added/removed/reclassified tools. |
| B2 | Third-party risk | Enumerates third-party servers against an allow-list. |
| B3 | Data loss prevention | Flags local-to-network tool compositions. |
| B4 | Privileged access | TCS threshold + execute-capable tool enumeration. |
| B5 | Audit and monitoring | Emits OCSF / CEF for SIEM ingestion; requires signed attestation. |
| B6 | AI-specific capability state | Detects graph changes under a stable host version. |

## Framework mapping

Every check is mapped to specific clauses in the three major AI
governance frameworks:

```bash
mcp-gov mappings list
mcp-gov mappings show iso42001
mcp-gov mappings show nist-ai-600-1
mcp-gov mappings show eu-ai-act
```

## Severity

Each check returns one of:

- `pass` — control satisfied.
- `info` — observation; not a policy violation.
- `warn` — attention required; not a blocker.
- `block` — policy violation; CI/pre-commit will fail.
