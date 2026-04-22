# Example MCP configurations

Each file mirrors one row of Table 3 of the companion paper
(§5.3, *The MCP Governance Gap*). Running ``mcp-gov attest`` on each
produces an attestation whose TCS matches the published value to the
decimal:

| File                           | Short | Paper TCS |
|--------------------------------|-------|-----------|
| c1-conservative.mcp.json       | C1    | 1.0       |
| c2-analyst.mcp.json            | C2    | 9.0       |
| c3-developer.mcp.json          | C3    | 13.5      |
| c4-full-stack.mcp.json         | C4    | 49.5      |
| c5-security-research.mcp.json  | C5    | 29.75     |

```bash
mcp-gov attest examples/c3-developer.mcp.json --host-id demo --out c3.attestation.json
# → emitted to c3.attestation.json, TCS = 13.5
```
