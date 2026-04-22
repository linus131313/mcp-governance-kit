"""mcp-governance-kit: runtime capability-state attestation for MCP agents."""

from __future__ import annotations

try:
    from mcp_governance_kit._version import __version__
except ImportError:  # pragma: no cover
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
