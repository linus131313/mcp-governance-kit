"""Parse MCP configuration files into server definitions.

Supports the three config shapes that make up the vast majority of the
real-world install base as of April 2026:

* Claude Desktop: ``claude_desktop_config.json``
* Claude Code: ``.mcp.json`` or ``.claude/settings.json``
* Cursor: ``~/.cursor/mcp.json``

All three use the same ``mcpServers`` shape, so a single parser covers
them; only the host-kind attribution differs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from mcp_governance_kit.attest.schema import ConfigSource, HostKind


@dataclass(frozen=True)
class RawServer:
    """A single ``mcpServers`` entry, pre-classification."""

    name: str
    command: str | None
    args: tuple[str, ...]
    env: dict[str, str]
    url: str | None
    transport_hint: str | None


@dataclass(frozen=True)
class CollectedConfig:
    """Result of parsing an MCP config file."""

    source: ConfigSource
    host_kind: HostKind
    servers: tuple[RawServer, ...]


_STDIO_KEYS = {"command", "args"}
_HTTP_KEYS = {"url", "transport"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _infer_host_kind(path: Path) -> HostKind:
    name = path.name.lower()
    parent = path.parent.name.lower() if path.parent.name else ""
    if "claude_desktop_config" in name:
        return HostKind.CLAUDE_DESKTOP
    if name == ".mcp.json" or parent == ".claude":
        return HostKind.CLAUDE_CODE
    if ".cursor" in str(path).lower() or "cursor" in parent:
        return HostKind.CURSOR
    return HostKind.CUSTOM


def _parse_server(name: str, raw: dict[str, object]) -> RawServer:
    command = raw.get("command")
    if command is not None and not isinstance(command, str):
        raise ValueError(f"{name}: 'command' must be a string")

    args_raw = raw.get("args", [])
    if not isinstance(args_raw, list):
        raise ValueError(f"{name}: 'args' must be a list")
    args = tuple(str(a) for a in args_raw)

    env_raw = raw.get("env", {}) or {}
    if not isinstance(env_raw, dict):
        raise ValueError(f"{name}: 'env' must be an object")
    env = {str(k): str(v) for k, v in env_raw.items()}

    url = raw.get("url")
    if url is not None and not isinstance(url, str):
        raise ValueError(f"{name}: 'url' must be a string")

    transport_hint = raw.get("transport")
    if transport_hint is not None and not isinstance(transport_hint, str):
        raise ValueError(f"{name}: 'transport' must be a string")

    return RawServer(
        name=name,
        command=command,
        args=args,
        env=env,
        url=url,
        transport_hint=transport_hint,
    )


def collect(path: Path, *, host_kind: HostKind | None = None) -> CollectedConfig:
    """Parse ``path`` into a :class:`CollectedConfig`.

    The function makes no network calls and never executes the configured
    commands; it reads the JSON and normalises it.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")

    servers_raw = data.get("mcpServers") or data.get("mcp_servers") or {}
    if not isinstance(servers_raw, dict):
        raise ValueError(f"{path}: 'mcpServers' must be an object")

    servers = tuple(
        _parse_server(name, srv) for name, srv in servers_raw.items() if isinstance(srv, dict)
    )

    return CollectedConfig(
        source=ConfigSource(path=str(path), sha256=_sha256(path)),
        host_kind=host_kind or _infer_host_kind(path),
        servers=servers,
    )
