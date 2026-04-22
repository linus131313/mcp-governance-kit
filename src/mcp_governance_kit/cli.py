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
from mcp_governance_kit.attest import (
    Attestation,
    SigstoreUnavailable,
    build_attestation,
    sign_attestation,
    verify_attestation,
)
from mcp_governance_kit.mappings import available_frameworks, load_mapping
from mcp_governance_kit.policy import Policy, evaluate
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


@app.command()
def attest(
    config_path: Annotated[Path, typer.Argument(help="Path to an MCP config file.")],
    host_id: Annotated[str, typer.Option("--host-id", help="Stable identifier for the host.")],
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Write attestation JSON to this path."),
    ] = None,
    sign: Annotated[bool, typer.Option("--sign/--no-sign", help="Sign with sigstore.")] = False,
) -> None:
    """Collect, classify, score, and (optionally) sign an attestation."""
    attestation: Attestation = build_attestation(config_path, host_id=host_id)
    if sign:
        try:
            attestation = sign_attestation(attestation)
        except SigstoreUnavailable as exc:
            typer.secho(f"sigstore unavailable: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=2) from exc

    payload = attestation.model_dump_json(indent=2)
    if out:
        out.write_text(payload + "\n", encoding="utf-8")
        typer.echo(f"wrote {out} (tcs={attestation.tcs.value})")
    else:
        typer.echo(payload)


@app.command()
def verify(
    attestation_path: Annotated[Path, typer.Argument(help="Attestation JSON to verify.")],
    expected_identity: Annotated[str | None, typer.Option("--expected-identity")] = None,
    expected_issuer: Annotated[str | None, typer.Option("--expected-issuer")] = None,
    allow_unsigned: Annotated[bool, typer.Option("--allow-unsigned/--require-signed")] = False,
) -> None:
    """Verify an attestation signature (and recompute its TCS)."""
    attestation = Attestation.model_validate_json(attestation_path.read_text(encoding="utf-8"))
    result = verify_attestation(
        attestation,
        expected_identity=expected_identity,
        expected_issuer=expected_issuer,
        allow_unsigned=allow_unsigned,
    )
    colour = typer.colors.GREEN if result.valid else typer.colors.RED
    status = "VALID" if result.valid else "INVALID"
    typer.secho(f"{status} ({result.signature_kind.value})", fg=colour)
    for reason in result.reasons:
        typer.echo(f"  - {reason}")
    if not result.valid:
        raise typer.Exit(code=1)


@app.command()
def check(
    attestation_path: Annotated[Path, typer.Argument(help="Attestation JSON to evaluate.")],
    policy_path: Annotated[Path, typer.Option("--policy", "-p", help="Policy YAML path.")],
    previous_path: Annotated[
        Path | None,
        typer.Option("--previous", help="Previous attestation, enables B1/B6 diff."),
    ] = None,
) -> None:
    """Evaluate B1–B6 against an attestation under the supplied policy."""
    attestation = Attestation.model_validate_json(attestation_path.read_text(encoding="utf-8"))
    previous = None
    if previous_path:
        previous = Attestation.model_validate_json(previous_path.read_text(encoding="utf-8"))
    policy = Policy.load(policy_path)
    report = evaluate(attestation, policy, previous=previous)
    console.print_json(data=report.model_dump())
    if report.blocked:
        raise typer.Exit(code=1)


mappings_app = typer.Typer(
    name="mappings",
    help="Framework-clause mappings for the breakpoint checks.",
    no_args_is_help=True,
)
app.add_typer(mappings_app)


@mappings_app.command("list")
def mappings_list() -> None:
    """List available framework mappings."""
    for f in available_frameworks():
        typer.echo(f)


@mappings_app.command("show")
def mappings_show(
    framework: Annotated[str, typer.Argument(help="Framework key, e.g. iso42001.")],
) -> None:
    """Print the mapping for ``framework`` as JSON."""
    console.print_json(data=load_mapping(framework))


if __name__ == "__main__":  # pragma: no cover
    app()
