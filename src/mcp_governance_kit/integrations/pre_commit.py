"""Pre-commit hook entry point.

Runs :func:`build_attestation` on each changed MCP config file and
evaluates the project's policy. Returns a non-zero exit code when any
check blocks, so the commit is refused.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from mcp_governance_kit.attest import build_attestation
from mcp_governance_kit.policy import Policy, evaluate


def _find_policy(repo_root: Path) -> Path | None:
    override = os.environ.get("MCP_GOV_POLICY")
    if override:
        return Path(override)
    for candidate in (
        repo_root / "policies" / "default.yaml",
        repo_root / ".mcp-governance.yaml",
    ):
        if candidate.exists():
            return candidate
    return None


def main(argv: list[str] | None = None) -> int:
    files = [Path(a) for a in (argv or sys.argv[1:]) if a]
    if not files:
        return 0

    repo_root = Path.cwd()
    policy_path = _find_policy(repo_root)
    if policy_path is None:
        print(
            "[mcp-gov] no policy found (looked for policies/default.yaml, "
            ".mcp-governance.yaml). Skipping check.",
            file=sys.stderr,
        )
        return 0

    policy = Policy.load(policy_path)
    exit_code = 0
    for path in files:
        try:
            att = build_attestation(path, host_id=os.environ.get("USER", "local"))
        except Exception as exc:  # pragma: no cover - user-facing
            print(f"[mcp-gov] failed to parse {path}: {exc}", file=sys.stderr)
            exit_code = 2
            continue
        report = evaluate(att, policy)
        status = "BLOCK" if report.blocked else ("WARN" if report.warnings else "OK")
        print(f"[mcp-gov] {path}: {status} tcs={att.tcs.value}")
        if report.blocked:
            for r in report.results:
                if r.severity.value == "block":
                    print(f"  - {r.check_id} {r.title}: {r.summary}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
