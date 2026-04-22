"""Common types for breakpoint checks."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    """The severity level of a :class:`CheckResult`."""

    PASS = "pass"
    INFO = "info"
    WARN = "warn"
    BLOCK = "block"


class CheckResult(BaseModel):
    """Structured outcome of a single breakpoint evaluation."""

    model_config = ConfigDict(extra="forbid")

    check_id: str = Field(pattern=r"^B[1-6]$")
    title: str
    severity: Severity
    summary: str
    details: list[str] = Field(default_factory=list)
    evidence: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.severity in (Severity.PASS, Severity.INFO)
