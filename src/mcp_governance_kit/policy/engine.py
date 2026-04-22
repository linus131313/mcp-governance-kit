"""YAML-driven policy engine.

A policy document declares numeric thresholds and allow-lists, and
whether any B-check is in ``block``, ``warn`` or ``allow`` mode. The
engine runs the breakpoint suite and aggregates a :class:`PolicyReport`.

Example policy::

    version: 1
    name: developer
    max_tcs: 20
    warn_tcs: 10
    third_party_allowlist:
      - "@modelcontextprotocol/server-github"
      - "@modelcontextprotocol/server-filesystem"
      - "shell-mcp"
    max_third_party: 6
    require_approval_for_execute: true
    require_approval_for_changes: false
    allow_exfil_paths: false
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from mcp_governance_kit.attest.schema import Attestation
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


class Policy(BaseModel):
    """Typed policy document."""

    model_config = ConfigDict(extra="forbid")

    version: int = 1
    name: str
    max_tcs: float | None = None
    warn_tcs: float | None = None
    third_party_allowlist: list[str] = Field(default_factory=list)
    max_third_party: int | None = None
    require_approval_for_execute: bool = False
    execute_approved: bool = False
    require_approval_for_changes: bool = False
    changes_approved: bool = False
    allow_exfil_paths: bool = False

    @classmethod
    def load(cls, path: Path) -> Policy:
        data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls.model_validate(data)


class PolicyReport(BaseModel):
    """Aggregate outcome of applying a policy to an attestation."""

    model_config = ConfigDict(extra="forbid")

    policy_name: str
    results: list[CheckResult]
    blocked: bool
    warnings: int
    policy_refs: list[str]

    @classmethod
    def from_results(cls, policy: Policy, results: list[CheckResult]) -> PolicyReport:
        blocked = any(r.severity is Severity.BLOCK for r in results)
        warnings = sum(1 for r in results if r.severity is Severity.WARN)
        return cls(
            policy_name=policy.name,
            results=results,
            blocked=blocked,
            warnings=warnings,
            policy_refs=[f"{policy.name}#v{policy.version}"],
        )


def evaluate(
    attestation: Attestation,
    policy: Policy,
    *,
    previous: Attestation | None = None,
) -> PolicyReport:
    """Run the six breakpoint checks with the supplied policy context."""
    results: list[CheckResult] = [
        b1_change(
            previous,
            attestation,
            changes_approved=policy.changes_approved,
            require_approval=policy.require_approval_for_changes,
        ),
        b2_thirdparty(
            attestation,
            allowlist=policy.third_party_allowlist,
            max_third_party=policy.max_third_party,
        ),
        b3_dlp(attestation, allow_exfil_paths=policy.allow_exfil_paths),
        b4_privilege(
            attestation,
            max_tcs=policy.max_tcs,
            warn_tcs=policy.warn_tcs,
            require_approval_for_execute=policy.require_approval_for_execute,
            execute_approved=policy.execute_approved,
        ),
        b5_audit(attestation),
        b6_capability_state(previous, attestation),
    ]
    return PolicyReport.from_results(policy, results)
