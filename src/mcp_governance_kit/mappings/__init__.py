"""Framework-clause mappings. Each B-check references the specific
clauses of ISO/IEC 42001, NIST AI 600-1, and the EU AI Act that it
addresses, so an auditor can cite the attestation as evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_HERE = Path(__file__).parent

_FRAMEWORK_FILES = {
    "iso42001": _HERE / "iso42001-annex-a.yaml",
    "nist-ai-600-1": _HERE / "nist-ai-600-1.yaml",
    "eu-ai-act": _HERE / "eu-ai-act.yaml",
}


def load_mapping(framework: str) -> dict[str, Any]:
    """Return the YAML mapping for ``framework`` as a dict."""
    path = _FRAMEWORK_FILES[framework]
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data


def available_frameworks() -> tuple[str, ...]:
    return tuple(_FRAMEWORK_FILES)


__all__ = ["available_frameworks", "load_mapping"]
