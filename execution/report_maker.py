"""Legacy compatibility adapter for canonical report rendering.

Use ``ai-audit approve`` and ``ai-audit render`` for new workflows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_audit.core.models import audit_result_from_dict
from ai_audit.core.rendering import render_deliverables


def generate_report(findings: dict[str, Any], data_package: dict[str, Any]) -> str:
    """Keep a small compatibility function without inventing compliance data."""
    status = findings.get("status", "needs_information")
    pending = findings.get("pending_questions", [])
    lines = [
        "# AI Audit — Relatório de compatibilidade",
        "",
        f"Status da análise: {status}",
        "",
        "## Limitações",
        "",
        "Este relatório foi gerado pelo adaptador legado. Use o pipeline canônico para o relatório final.",
        "",
        "## Perguntas pendentes",
        "",
    ]
    lines.extend(f"- {item}" for item in pending or ["Nenhuma registrada."])
    return "\n".join(lines) + "\n"


def load_json(filepath: str) -> dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Audit — legacy report adapter")
    parser.add_argument("--workspace", required=True, help="Workspace com working/audit_result.json")
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()
    try:
        root = Path(args.workspace).resolve()
        result_path = root / "working" / "audit_result.json"
        result = audit_result_from_dict(load_json(str(result_path)))
        outputs = render_deliverables(result, str(root / "output"), draft=args.draft)
        print("\n".join(outputs))
        return 0
    except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Error generating report: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
