"""Smoke and behavioural tests for the six breakpoint checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_governance_kit.attest import build_attestation, sign_attestation
from mcp_governance_kit.attest.schema import Signature, SignatureKind
from mcp_governance_kit.breakpoints import (
    CheckResult,
    Severity,
    b1_change,
    b2_thirdparty,
    b3_dlp,
    b4_privilege,
    b5_audit,
    b6_capability_state,
)

EXAMPLES = Path(__file__).resolve().parent.parent.parent / "examples"


@pytest.fixture
def c3() -> object:
    return build_attestation(EXAMPLES / "c3-developer.mcp.json", host_id="h")


@pytest.fixture
def c4() -> object:
    return build_attestation(EXAMPLES / "c4-full-stack.mcp.json", host_id="h")


def _assert_result(result: CheckResult, check_id: str) -> None:
    assert result.check_id == check_id
    assert isinstance(result.severity, Severity)
    assert result.summary


def test_b1_pass_on_identical_attestations(c3) -> None:  # type: ignore[no-untyped-def]
    result = b1_change(c3, c3)
    _assert_result(result, "B1")
    assert result.severity is Severity.PASS


def test_b1_warn_on_upgrade(c3, c4) -> None:  # type: ignore[no-untyped-def]
    result = b1_change(c3, c4)
    assert result.severity is Severity.WARN
    assert result.evidence["added"] > 0


def test_b1_block_when_approval_required(c3, c4) -> None:  # type: ignore[no-untyped-def]
    result = b1_change(c3, c4, require_approval=True)
    assert result.severity is Severity.BLOCK


def test_b2_warn_on_unknown_third_party(c3) -> None:  # type: ignore[no-untyped-def]
    result = b2_thirdparty(c3, allowlist=[])
    assert result.severity is Severity.WARN


def test_b2_block_on_too_many(c4) -> None:  # type: ignore[no-untyped-def]
    result = b2_thirdparty(c4, max_third_party=2)
    assert result.severity is Severity.BLOCK


def test_b3_flags_local_to_network_path(c3) -> None:  # type: ignore[no-untyped-def]
    result = b3_dlp(c3)
    assert result.severity is Severity.WARN
    assert result.evidence["path_count"] > 0


def test_b4_block_when_over_max_tcs(c4) -> None:  # type: ignore[no-untyped-def]
    result = b4_privilege(c4, max_tcs=20)
    assert result.severity is Severity.BLOCK


def test_b4_info_within_thresholds(c3) -> None:  # type: ignore[no-untyped-def]
    result = b4_privilege(c3, max_tcs=100, warn_tcs=100)
    assert result.severity is Severity.INFO


def test_b5_warn_unsigned(c3) -> None:  # type: ignore[no-untyped-def]
    result = b5_audit(c3)
    assert result.severity is Severity.WARN
    assert "cef" in result.evidence


def test_b5_pass_when_signed(c3) -> None:  # type: ignore[no-untyped-def]
    signed = c3.model_copy(
        update={"signature": Signature(kind=SignatureKind.SIGSTORE_KEYLESS, bundle="fake==")}
    )
    _ = sign_attestation  # referenced for completeness of the sign path
    result = b5_audit(signed)
    assert result.severity is Severity.PASS


def test_b6_warn_when_graph_changes_under_stable_host(c3) -> None:  # type: ignore[no-untyped-def]
    mutated = c3.model_copy(update={"tools": c3.tools[:-1]})
    result = b6_capability_state(c3, mutated)
    assert result.severity is Severity.WARN


def test_b6_pass_when_stable(c3) -> None:  # type: ignore[no-untyped-def]
    result = b6_capability_state(c3, c3)
    assert result.severity is Severity.PASS
