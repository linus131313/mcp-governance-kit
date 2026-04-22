# CI integration

The kit ships a composite GitHub Action at the root of the repository.

## Minimal workflow

`.github/workflows/mcp-governance.yml`:

```yaml
name: MCP Governance
on:
  pull_request:
    paths: [".mcp.json", "policies/*.yaml"]

permissions:
  id-token: write       # required for sigstore keyless
  contents: read

jobs:
  attest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: linus131313/mcp-governance-kit@v0
        with:
          config-path: .mcp.json
          policy-path: policies/default.yaml
          fail-on-warn: "false"
```

## What the action does

1. Installs `mcp-governance-kit[sign]`.
2. Runs `mcp-gov attest` with `--sign` (sigstore keyless via GitHub OIDC).
3. Uploads the TCS and attestation path as step outputs.
4. Runs `mcp-gov check` against the supplied policy.
5. Writes the JSON report to the GitHub Actions job summary.
6. Fails the job on `BLOCK`; also fails on `WARN` when `fail-on-warn` is true.

## Attestation as a release artefact

To publish the signed attestation as part of a release, add a follow-up
step:

```yaml
      - uses: softprops/action-gh-release@v2
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: ${{ steps.run.outputs.attestation-path }}
```
