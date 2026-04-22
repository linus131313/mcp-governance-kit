"""Regenerate the on-disk JSON Schema from the pydantic model.

Run manually when :mod:`mcp_governance_kit.attest.schema` changes::

    python scripts/export_schema.py

CI verifies that the checked-in file matches the regenerated output so
schema drift is never silent.
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp_governance_kit.attest.schema import export_json_schema

OUT = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "mcp_governance_kit"
    / "attest"
    / "schemas"
    / "attestation-v0.schema.json"
)


def main() -> None:
    schema = export_json_schema()
    OUT.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parent.parent.parent.parent.parent)}")


if __name__ == "__main__":
    main()
