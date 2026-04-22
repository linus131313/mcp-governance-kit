"""Integration hooks — pre-commit and Claude Code."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from mcp_governance_kit.integrations.claude_code_hook import main as hook_main
from mcp_governance_kit.integrations.pre_commit import main as pre_commit_main

ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES = ROOT / "examples"
POLICIES = ROOT / "policies"


def test_pre_commit_pass_on_c3(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / "repo"
    (workspace / "policies").mkdir(parents=True)
    (workspace / "policies" / "default.yaml").write_text(
        (POLICIES / "developer.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    mcp_json = workspace / ".mcp.json"
    mcp_json.write_text(
        (EXAMPLES / "c3-developer.mcp.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.chdir(workspace)
    rc = pre_commit_main([str(mcp_json)])
    assert rc == 0


def test_pre_commit_blocks_full_stack_under_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "repo"
    (workspace / "policies").mkdir(parents=True)
    (workspace / "policies" / "default.yaml").write_text(
        (POLICIES / "default.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    mcp_json = workspace / ".mcp.json"
    mcp_json.write_text(
        (EXAMPLES / "c4-full-stack.mcp.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.chdir(workspace)
    rc = pre_commit_main([str(mcp_json)])
    assert rc == 1


def test_claude_code_hook_allows_when_no_workspace_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    event = {"tool_name": "list_issues", "cwd": str(tmp_path)}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(event)))
    rc = hook_main()
    assert rc == 0
    out = capsys.readouterr().out
    assert json.loads(out)["decision"] == "allow"
