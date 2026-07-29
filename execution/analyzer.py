"""Legacy compatibility adapter for the canonical risk screening module.

This file no longer fabricates a compliance score. New workflows should use
``ai-audit analyze-opportunities`` directly.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from ai_audit.core.models import Opportunity, to_dict
from ai_audit.modules.risk_assessment import assess_all


def analyze_risks(data_package: dict[str, Any]) -> dict[str, Any]:
    """Screen normalized opportunities without claiming legal compliance."""
    raw_opportunities = data_package.get("opportunities", [])
    if not raw_opportunities:
        return {
            "status": "needs_information",
            "risk_matrix": [],
            "compliance_score": None,
            "mitigation_strategies": [],
            "pending_questions": ["Nenhuma oportunidade normalizada foi fornecida para avaliação de risco."],
        }

    opportunities = [Opportunity(**item) for item in raw_opportunities]
    risks = assess_all(opportunities, data_package.get("jurisdictions", ["BR"]))
    risk_matrix = []
    mitigation_strategies = []
    for assessment in risks:
        for risk in assessment.risks:
            risk_matrix.append({
                "area": risk.get("category", "unknown"),
                "risk": risk.get("risk", ""),
                "impact": risk.get("impact", "unknown"),
                "likelihood": risk.get("likelihood", "unknown"),
                "opportunity_id": assessment.opportunity_id,
            })
        mitigation_strategies.extend(item.get("action", "") for item in assessment.mitigations)

    return {
        "status": "screened",
        "risk_matrix": risk_matrix,
        "compliance_score": None,
        "mitigation_strategies": mitigation_strategies,
        "risk_assessments": to_dict(risks),
        "legal_review_required": any(item.requires_legal_review for item in risks),
    }


def load_data_package(filename: str = "data_package.json") -> dict[str, Any]:
    path = os.path.join(".tmp", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data package not found at {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_findings(findings: dict[str, Any], filename: str = "risk_findings.json") -> None:
    os.makedirs(".tmp", exist_ok=True)
    with open(os.path.join(".tmp", filename), "w", encoding="utf-8") as file:
        json.dump(findings, file, ensure_ascii=False, indent=2)
    print(f"Saved {filename} to .tmp")


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Audit — legacy risk adapter")
    parser.add_argument("--data-package", default="data_package.json")
    args = parser.parse_args()
    try:
        save_findings(analyze_risks(load_data_package(args.data_package)))
        return 0
    except (FileNotFoundError, ValueError, TypeError) as exc:
        print(f"Error during analysis: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
