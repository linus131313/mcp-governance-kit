# Contributing to mcp-governance-kit

Thank you for considering a contribution. This project is a companion
implementation to the academic paper [*The MCP Governance Gap*](paper/governance-speed-gap.pdf);
contributions that strengthen the paper's empirical claims, broaden
framework coverage, or harden the attestation primitive are especially
welcome.

## Ground rules

1. **Paper integrity.** Changes to the TCS algorithm in `src/mcp_governance_kit/tcs/`
   must keep `tests/unit/test_tcs_score.py` green — those tests pin the
   numerical values reported in Table 3 of the paper. If you believe a
   weight change is warranted, open an issue first so we can discuss
   whether it requires a paper revision.

2. **Spec first.** The attestation format is defined in [`SPEC.md`](SPEC.md).
   Breaking changes to the schema require a version bump
   (`attestation-v1.schema.json`) and a spec update, not a silent edit.

3. **Typed and tested.** All new code must pass `ruff`, `mypy --strict`,
   and have test coverage ≥ 90 % for the lines it touches.

## Development setup

```bash
git clone https://github.com/linus131313/mcp-governance-kit
cd mcp-governance-kit
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev,all]"

# run the quality gates
ruff check .
ruff format --check .
mypy src
pytest
```

## Commit and PR hygiene

- One logical change per commit, imperative mood (`Add B4 privilege check`).
- PRs linked to an issue where possible.
- The CI workflow must pass; do not disable checks to merge.
- For security-relevant changes, please read [`SECURITY.md`](SECURITY.md)
  first.

## Releasing

Releases are tagged `v*.*.*` and publish to PyPI via GitHub OIDC trusted
publishing. Only maintainers can cut a release; the flow is documented in
`.github/workflows/release.yml`.
