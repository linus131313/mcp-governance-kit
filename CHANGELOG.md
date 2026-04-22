# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-22

First public alpha release. Complete reference implementation of the
Capability-State Attestation primitive described in SPEC v0 and of the
companion paper *The MCP Governance Gap* (Teklenburg, 2026).

### Added

- **TCS library** (`mcp_governance_kit.tcs`) reproducing Table 3 of the
  paper: C1=1.0, C2=9.0, C3=13.5, C4=49.5, C5=29.75, R1=2.0, R2=5.0,
  R3=7.0, R4=15.0. Sensitivity analysis over the 48-point reweighting
  grid with all headline invariants matching the paper.
- **Attestation pipeline** (`mcp_governance_kit.attest`): collect,
  classify, score, sign (sigstore keyless), verify. Versioned JSON
  Schema with a CI drift guard.
- **Breakpoints** (`mcp_governance_kit.breakpoints`): B1 change
  management, B2 third-party risk, B3 data loss prevention, B4
  privileged access, B5 audit and monitoring, B6 capability state.
- **Policy engine** (`mcp_governance_kit.policy`) with YAML-driven
  `Policy` and aggregated `PolicyReport`. Three built-in policies:
  default, developer, restricted.
- **Framework mappings** (`mcp_governance_kit.mappings`): ISO/IEC
  42001 Annex A, NIST AI 600-1, EU AI Act. Each B-check maps to the
  specific clauses it addresses.
- **Integrations**: composite GitHub Action at `action.yml`,
  `.pre-commit-hooks.yaml`, and Claude Code `PreToolUse` hook.
- **CLI**: `mcp-gov score | tcs | attest | verify | check | mappings`.
- **Documentation**: mkdocs-material site deployed to GitHub Pages on
  push to `main` with Auditor Handbook, CI guide, policy-authoring
  guide, TCS/Attestation/Breakpoints concept pages.
- **Paper**: archived at `paper/governance-speed-gap.pdf` with
  `CITATION.cff`.

### Quality gates

- 54 tests green across 3 OSes × 3 Python versions in CI.
- mypy `--strict` clean, ruff clean, coverage ~82 %.
- CodeQL weekly + on every PR.
- Dependabot weekly for pip and GitHub Actions.
