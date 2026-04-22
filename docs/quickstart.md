# Quickstart

## 1. Install

```bash
pip install 'mcp-governance-kit[sign]'
```

## 2. Reproduce the paper

The tool ships the paper's reference configurations under `examples/`.
Running the TCS reproduction prints Table 3:

```bash
mcp-gov tcs reference
```

## 3. Attest your own configuration

Point the tool at whichever MCP config file you use:

```bash
# Claude Code
mcp-gov attest .mcp.json --host-id $(hostname) --out att.json

# Claude Desktop
mcp-gov attest ~/.config/claude-desktop/claude_desktop_config.json --host-id $(hostname) --out att.json
```

Use `--sign` to produce a sigstore-keyless signature in CI
(the GitHub OIDC flow) or via interactive OAuth locally.

## 4. Evaluate a policy

```bash
mcp-gov check att.json --policy policies/default.yaml
```

The tool prints a JSON report with one entry per breakpoint (B1 through
B6), aggregated `blocked` / `warnings`, and the framework-clause IDs
each check addresses.

## 5. Wire up CI

Add the following step to `.github/workflows/governance.yml`:

```yaml
- uses: linus131313/mcp-governance-kit@v0
  with:
    config-path: .mcp.json
    policy-path: policies/default.yaml
```

The action attests, signs via GitHub OIDC, enforces the policy, and
writes a report into the GitHub Action job summary.
