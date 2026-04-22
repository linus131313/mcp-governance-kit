"""Command-line interface for mcp-governance-kit.

Only the top-level skeleton is implemented at this stage. Subcommands are
filled in by subsequent modules (``score``, ``attest``, ``check``, ``verify``).
"""

from __future__ import annotations

import typer

from mcp_governance_kit import __version__

app = typer.Typer(
    name="mcp-gov",
    help="Runtime capability-state attestation for Model Context Protocol agents.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def version() -> None:
    """Print the installed mcp-governance-kit version."""
    typer.echo(__version__)


if __name__ == "__main__":  # pragma: no cover
    app()
