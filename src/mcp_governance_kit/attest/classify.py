"""Classify raw MCP server definitions into (reach, action, third_party)
and produce full :class:`ToolRecord` entries.

The built-in catalogue covers the servers shipped in
``modelcontextprotocol/servers`` and the most common community servers
referenced in the paper's incident corpus (github, supabase, aws, docker,
nmap, metasploit, sqlite, fetch, filesystem). Unknown servers fall back
to conservative defaults and an ``unresolved`` tool record so the
attestation never silently under-reports privilege.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mcp_governance_kit.attest.collect import RawServer
from mcp_governance_kit.attest.schema import ServerRecord, ToolRecord, Transport
from mcp_governance_kit.tcs.models import Action, Reach


@dataclass(frozen=True)
class ServerProfile:
    """Classification profile for a known server."""

    identity: str
    reach: Reach
    action: Action
    third_party: bool
    default_tool_name: str = "tool"


_FIRST_PARTY_PREFIXES = (
    "@modelcontextprotocol/",
    "anthropic-mcp-",
    "mcp-server-",  # canonical Anthropic-maintained reference servers
)


_CATALOGUE: dict[str, ServerProfile] = {
    # Reference servers. The paper treats the filesystem reference server
    # as first-party to the host vendor (bundled in default install flows),
    # while sqlite and fetch are treated as third-party because they are
    # opt-in additions a user brings themselves. See Table 3 of the paper.
    "@modelcontextprotocol/server-filesystem": ServerProfile(
        "@modelcontextprotocol/server-filesystem", Reach.LOCAL, Action.WRITE, False, "filesystem"
    ),
    "@modelcontextprotocol/server-sqlite": ServerProfile(
        "@modelcontextprotocol/server-sqlite", Reach.LOCAL, Action.WRITE, True, "sqlite"
    ),
    "@modelcontextprotocol/server-fetch": ServerProfile(
        "@modelcontextprotocol/server-fetch", Reach.NETWORK, Action.READ, True, "fetch"
    ),
    "@modelcontextprotocol/server-github": ServerProfile(
        "@modelcontextprotocol/server-github", Reach.NETWORK, Action.WRITE, True, "github"
    ),
    # Third-party servers named in the paper's incident and example set
    "supabase-mcp": ServerProfile("supabase-mcp", Reach.NETWORK, Action.WRITE, True, "supabase"),
    "aws-mcp": ServerProfile("aws-mcp", Reach.NETWORK, Action.EXECUTE, True, "aws"),
    "docker-mcp": ServerProfile("docker-mcp", Reach.LOCAL, Action.EXECUTE, True, "docker"),
    "nmap-mcp": ServerProfile("nmap-mcp", Reach.NETWORK, Action.EXECUTE, True, "nmap"),
    "metasploit-mcp": ServerProfile(
        "metasploit-mcp", Reach.NETWORK, Action.EXECUTE, True, "metasploit"
    ),
    "shell-mcp": ServerProfile("shell-mcp", Reach.LOCAL, Action.EXECUTE, True, "shell"),
}


@dataclass(frozen=True)
class Classification:
    """Extensible override table passed to :func:`classify_server`."""

    extra: dict[str, ServerProfile] = field(default_factory=dict)


def _identity_of(raw: RawServer) -> str:
    """Derive a stable identity string for a raw server definition.

    For npx-style invocations we extract the first non-flag positional
    argument that looks like a package name (scoped, path-like, mcp-named,
    or script file). This matches the way Claude Desktop configs spell
    servers in the wild.
    """
    if raw.url:
        return raw.url
    if raw.command:
        for a in raw.args:
            if a.startswith("-"):
                continue
            if (
                a.startswith("@")
                or "/" in a
                or a.endswith((".py", ".js", ".ts", ".mjs"))
                or a.endswith("-mcp")
                or a.startswith("mcp-")
                or "mcp" in a
            ):
                return a
        return " ".join([raw.command, *raw.args])
    return raw.name


def _is_first_party(identity: str) -> bool:
    return any(identity.startswith(p) for p in _FIRST_PARTY_PREFIXES)


def _transport_of(raw: RawServer) -> Transport:
    if raw.url:
        if raw.transport_hint == "sse":
            return Transport.SSE
        return Transport.STREAMABLE_HTTP
    return Transport.STDIO


def classify_server(raw: RawServer, overrides: Classification | None = None) -> ToolRecord:
    """Classify a raw server into a single representative :class:`ToolRecord`.

    The built-in catalogue maps well-known server identities to known
    profiles. Unknown servers get a conservative fallback
    (``reach=network`` if it looks networked, ``action=write``,
    ``third_party=True``) so the attestation does not under-report.
    """
    identity = _identity_of(raw)
    profile: ServerProfile | None = None

    if overrides:
        profile = overrides.extra.get(identity) or overrides.extra.get(raw.name)
    if profile is None:
        profile = _CATALOGUE.get(identity)

    if profile is None:
        # Conservative fallback
        reach = Reach.NETWORK if raw.url else Reach.LOCAL
        action = Action.EXECUTE if raw.command in ("bash", "sh", "pwsh", "cmd") else Action.WRITE
        third_party = not _is_first_party(identity)
        resolved = False
        tool_name = raw.name
        version = None
    else:
        reach = profile.reach
        action = profile.action
        third_party = profile.third_party
        resolved = True
        tool_name = profile.default_tool_name
        version = None

    # Argument-level overrides: --read-only downgrades a write server
    # to read-only, matching the filesystem-ro case (C1 in the paper).
    if "--read-only" in raw.args or "-r" in raw.args:
        action = Action.READ
        if tool_name == "filesystem":
            tool_name = "filesystem-ro"

    return ToolRecord(
        name=tool_name,
        server=ServerRecord(
            name=raw.name,
            transport=_transport_of(raw),
            identity=identity,
            version=version,
            third_party=third_party,
        ),
        reach=reach,
        action=action,
        description=None,
        resolved=resolved,
    )
