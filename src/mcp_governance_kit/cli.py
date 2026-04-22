"""Command-line interface for mcp-governance-kit.

The top-level app exposes these sub-apps:

* ``mcp-gov tcs`` — scoring and sensitivity (paper §5.3).
* ``mcp-gov attest`` (planned).
* ``mcp-gov check`` (planned).
* ``mcp-gov verify`` (planned).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from mcp_governance_kit import __version__
from mcp_governance_kit.tcs import (
    REFERENCE,
    Config,
    SensitivityReport,
    reweighting_grid,
    sensitivity_analysis,
    tcs,
)

app = typer.Typer(
    name="mcp-gov",
    help="Runtime capability-state attestation for Model Context Protocol agents.",
    no_args_is_help=True,
    add_completion=False,
)

tcs_app = typer.Typer(
    name="tcs",
    help="Tool Graph Capability Score — compute, compare, reproduce Table 3 of the paper.",
    no_args_is_help=True,
)
app.add_typer(tcs_app)

console = Console()


@app.command()
def version() -> None:
    """Print the installed mcp-governance-kit version."""
    typer.echo(__version__)


@tcs_app.command("reference")
def tcs_reference() -> None:
    """Reproduce Table 3 of the paper (C1–C5 and R1–R4)."""
    table = Table(title="Tool Graph Capability Score — Table 3 reproduction")
    table.add_column("Short")
    table.add_column("Label", overflow="fold")
    table.add_column("Tools", justify="right")
    table.add_column("3rd-party", justify="right")
    table.add_column("TCS", justify="right")
    for cfg in REFERENCE:
        table.add_row(
            cfg.short,
            cfg.label,
            str(len(cfg.tools)),
            str(cfg.third_party_count),
            f"{tcs(cfg):.2f}".rstrip("0").rstrip(".") or "0",
        )
    console.print(table)


@tcs_app.command("score")
def tcs_score(
    config_path: Annotated[Path, typer.Argument(help="Path to a Config JSON file.")],
) -> None:
    """Score a single configuration supplied as JSON."""
    data = json.loads(config_path.read_text(encoding="utf-8"))
    cfg = Config.model_validate(data)
    console.print_json(
        data={
            "short": cfg.short,
            "label": cfg.label,
            "tools": len(cfg.tools),
            "third_party_count": cfg.third_party_count,
            "tcs": tcs(cfg),
        }
    )


@tcs_app.command("sensitivity")
def tcs_sensitivity() -> None:
    """Run the 48-point sensitivity grid over the reference configurations."""
    report: SensitivityReport = sensitivity_analysis(REFERENCE, grid=reweighting_grid())
    console.print_json(data=report.model_dump())


if __name__ == "__main__":  # pragma: no cover
    app()
