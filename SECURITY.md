# Security Policy

## Supported versions

While the project is in alpha (0.x), only the latest minor release is
security-supported. Once the project reaches 1.0 this policy will be
revised.

| Version | Supported |
|---------|-----------|
| 0.x     | :white_check_mark: latest minor only |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-relevant bugs.

Instead, report via one of:

1. GitHub's private vulnerability reporting on this repository
   (Security → Report a vulnerability).
2. Email **hey@linus-teklenburg.de** with subject
   `[mcp-governance-kit security]`.

We aim to acknowledge reports within 72 hours and to release a fix or
mitigation within 30 days for high-severity issues. Credit is given to
reporters unless anonymity is requested.

## Scope

In scope:

- Authentication and signature-verification flaws in the attestation
  pipeline (`src/mcp_governance_kit/attest/`).
- Policy-engine bypasses.
- Any issue allowing an attacker to produce a valid signed attestation
  that misrepresents the underlying capability graph.

Out of scope:

- Vulnerabilities in third-party MCP servers themselves (report to the
  upstream project).
- Vulnerabilities in the sigstore or cosign infrastructure (report
  upstream).
