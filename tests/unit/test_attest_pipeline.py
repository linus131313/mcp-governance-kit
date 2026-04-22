"""End-to-end tests for the attestation pipeline.

The example configurations in ``examples/`` mirror Table 3 of the paper.
``build_attestation`` must reproduce the published TCS values exactly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mcp_governance_kit.attest import (
    HostKind,
    SignatureKind,
    build_attestation,
    verify_attestation,
)
from mcp_governance_kit.cli import app

EXAMPLES = Path(__file__).resolve().parent.parent.parent / "examples"

PAPER_TCS: dict[str, float] = {
    "c1-conservative": 1.0,
    "c2-analyst": 9.0,
    "c3-developer": 13.5,
    "c4-full-stack": 49.5,
    "c5-security-research": 29.75,
}


@pytest.mark.parametrize(("slug", "expected_tcs"), list(PAPER_TCS.items()))
def test_example_config_reproduces_paper_tcs(slug: str, expected_tcs: float) -> None:
    path = EXAMPLES / f"{slug}.mcp.json"
    att = build_attestation(path, host_id=f"test-{slug}")
    assert att.tcs.value == pytest.approx(expected_tcs, abs=1e-9), (
        f"{slug}: expected TCS {expected_tcs}, got {att.tcs.value}"
    )
    assert att.config_source.path == str(path)
    assert att.host.kind in set(HostKind)


def test_unsigned_attestation_rejected_by_default() -> None:
    att = build_attestation(EXAMPLES / "c1-conservative.mcp.json", host_id="h1")
    assert att.signature.kind is SignatureKind.UNSIGNED
    result = verify_attestation(att)
    assert result.valid is False
    assert "unsigned-not-allowed" in result.reasons


def test_unsigned_allowed_when_explicit() -> None:
    att = build_attestation(EXAMPLES / "c1-conservative.mcp.json", host_id="h1")
    result = verify_attestation(att, allow_unsigned=True)
    assert result.valid is True


def test_cli_attest_then_verify(tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "c3.attestation.json"
    result = runner.invoke(
        app,
        [
            "attest",
            str(EXAMPLES / "c3-developer.mcp.json"),
            "--host-id",
            "ci-runner",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert out.exists()
    assert "tcs=13.5" in result.stdout

    result2 = runner.invoke(app, ["verify", str(out), "--allow-unsigned"])
    assert result2.exit_code == 0, result2.stdout
    assert "VALID" in result2.stdout
