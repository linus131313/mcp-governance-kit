"""Pydantic models for the TCS domain: Tool, Config, Reach, Action.

The canonical enum members intentionally match the string values used in
the companion paper and in the original ``capability_score.py`` so that
config JSON files remain human-readable and portable.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Reach(StrEnum):
    """Where a tool can reach."""

    LOCAL = "local"
    NETWORK = "network"


class Action(StrEnum):
    """Action-level privilege a tool grants."""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"


class Tool(BaseModel):
    """A single MCP tool in a configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    reach: Reach
    action: Action
    third_party: bool = False


class Config(BaseModel):
    """A named tool graph — what a host can reach at a point in time."""

    model_config = ConfigDict(extra="forbid")

    label: str
    short: str = Field(min_length=1, max_length=8)
    tools: list[Tool]

    @property
    def third_party_count(self) -> int:
        return sum(1 for t in self.tools if t.third_party)
