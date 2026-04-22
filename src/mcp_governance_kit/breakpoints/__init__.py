"""Control-breakpoint checks (B1–B6 from Table 6 of the paper).

Each check operationalises one control family that the paper identifies
as silently broken under an MCP-native agent architecture:

* B1 — change management (ISO 27001 A.8.32, COBIT BAI06)
* B2 — third-party risk (ISO 27001 A.5.19, NIST SP 800-161)
* B3 — data loss prevention (ISO 27001 A.8.12)
* B4 — privileged access (ISO 27001 A.8.2, NIST AC-6)
* B5 — audit and monitoring (ISO 27001 A.8.15, NIST AU family)
* B6 — AI-specific capability state (ISO 42001 A.6, NIST AI 600-1)
"""

from __future__ import annotations

from mcp_governance_kit.breakpoints.b1_change import b1_change
from mcp_governance_kit.breakpoints.b2_thirdparty import b2_thirdparty
from mcp_governance_kit.breakpoints.b3_dlp import b3_dlp
from mcp_governance_kit.breakpoints.b4_privilege import b4_privilege
from mcp_governance_kit.breakpoints.b5_audit import b5_audit
from mcp_governance_kit.breakpoints.b6_capability_state import b6_capability_state
from mcp_governance_kit.breakpoints.base import CheckResult, Severity

ALL_CHECKS = ("B1", "B2", "B3", "B4", "B5", "B6")

__all__ = [
    "ALL_CHECKS",
    "CheckResult",
    "Severity",
    "b1_change",
    "b2_thirdparty",
    "b3_dlp",
    "b4_privilege",
    "b5_audit",
    "b6_capability_state",
]
