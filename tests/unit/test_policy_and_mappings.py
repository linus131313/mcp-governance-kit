"""Policy engine end-to-end and framework-mapping integrity tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_governance_kit.attest import build_attestation
from mcp_governance_kit.breakpoints import ALL_CHECKS
from mcp_governance_kit.mappings import available_frameworks, load_mapping
from mcp_governance_kit.policy import Policy, evaluate

ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES = ROOT / "examples"
POLICIES = ROOT / "policies"


def test_default_policy_blocks_full_stack_attestation() -> None:
    att = build_attestation(EXAMPLES / "c4-full-stack.mcp.json", host_id="dev")
    policy = Policy.load(POLICIES / "default.yaml")
    report = evaluate(att, policy)
    assert report.blocked is True
    assert len(report.results) == 6


def test_developer_policy_permits_c3() -> None:
    att = build_attestation(EXAMPLES / "c3-developer.mcp.json", host_id="dev")
    policy = Policy.load(POLICIES / "developer.yaml")
    report = evaluate(att, policy)
    assert report.blocked is False, report.model_dump()


def test_restricted_policy_blocks_developer_config() -> None:
    att = build_attestation(EXAMPLES / "c3-developer.mcp.json", host_id="analyst")
    policy = Policy.load(POLICIES / "restricted.yaml")
    report = evaluate(att, policy)
    assert report.blocked is True


@pytest.mark.parametrize("framework", ["iso42001", "nist-ai-600-1", "eu-ai-act"])
def test_mapping_covers_all_six_checks(framework: str) -> None:
    mapping = load_mapping(framework)
    assert "checks" in mapping
    assert set(mapping["checks"]) == set(ALL_CHECKS)
    for cid in ALL_CHECKS:
        entry = mapping["checks"][cid]
        assert entry["title"]
        assert entry["clauses"]


def test_available_frameworks_lists_all_three() -> None:
    frameworks = available_frameworks()
    assert set(frameworks) == {"iso42001", "nist-ai-600-1", "eu-ai-act"}
