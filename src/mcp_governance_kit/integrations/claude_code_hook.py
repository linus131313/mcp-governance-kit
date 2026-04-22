"""Claude Code ``PreToolUse`` hook.

Installed as a JSON-based hook in ``~/.claude/settings.json``, this
script reads the pending tool-use event from stdin, looks up the tool
in the current attestation for the workspace, and permits or denies
the call based on the active policy.

Hook wire format (PreToolUse):

    {
      "tool_name": "<string>",
      "tool_input": {...},
      "session_id": "<string>",
      "transcript_path": "<path>",
      "cwd": "<path>"
    }

The hook writes a JSON response to stdout with a ``decision`` field
("allow" | "deny") and a short reason. A non-zero exit code converts to
a denial with Claude Code's default behaviour.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from mcp_governance_kit.attest import Attestation
from mcp_governance_kit.breakpoints import Severity, b4_privilege
from mcp_governance_kit.policy import Policy


def _load_context(cwd: Path) -> tuple[Attestation | None, Policy | None]:
    att_path = cwd / ".mcp-governance" / "attestation.json"
    policy_path = cwd / ".mcp-governance" / "policy.yaml"
    attestation = (
        Attestation.model_validate_json(att_path.read_text(encoding="utf-8"))
        if att_path.exists()
        else None
    )
    policy = Policy.load(policy_path) if policy_path.exists() else None
    return attestation, policy


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow", "reason": "no event"}))
        return 0

    cwd = Path(event.get("cwd") or ".")
    attestation, policy = _load_context(cwd)
    tool_name = event.get("tool_name", "")

    if attestation is None or policy is None:
        print(json.dumps({"decision": "allow", "reason": "no attestation in workspace"}))
        return 0

    bound = {t.name for t in attestation.tools}
    if tool_name and tool_name not in bound and tool_name.split("__")[-1] not in bound:
        print(
            json.dumps(
                {
                    "decision": "deny",
                    "reason": (
                        f"tool '{tool_name}' not present in current attestation "
                        f"({attestation.attestation_id}); re-attest with mcp-gov attest"
                    ),
                }
            )
        )
        return 2

    # Re-run the privilege check with the attestation's stored TCS value.
    priv = b4_privilege(
        attestation,
        max_tcs=policy.max_tcs,
        warn_tcs=policy.warn_tcs,
        require_approval_for_execute=policy.require_approval_for_execute,
        execute_approved=policy.execute_approved,
    )
    if priv.severity is Severity.BLOCK:
        print(
            json.dumps(
                {
                    "decision": "deny",
                    "reason": f"B4 blocked: {priv.summary}",
                }
            )
        )
        return 2

    print(json.dumps({"decision": "allow", "reason": "within policy"}))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
