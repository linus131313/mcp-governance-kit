"""Smoke test — the package imports and the CLI runs."""

from __future__ import annotations

from typer.testing import CliRunner

from mcp_governance_kit import __version__
from mcp_governance_kit.cli import app


def test_version_is_set() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_cli_version_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
