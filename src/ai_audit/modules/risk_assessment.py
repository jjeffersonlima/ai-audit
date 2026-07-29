"""Risk gate for automation and AI opportunities.

This is a conservative screening layer, not legal advice. It requires the
agent or a qualified reviewer to provide the normalized facts and evidence.
"""

from __future__ import annotations

from ..core.models import Opportunity, RiskAssessment


HIGH_IMPACT_CATEGORIES = {"health", "financial", "biometric", "children", "employment", "credit"}


def assess_opportunity_risk(opportunity: Opportunity, jurisdictions: list[str]) -> RiskAssessment:
    assessment_id = f"R-{opportunity.opportunity_id.removeprefix('OP-')}"
    if not opportunity.involves_ai and not opportunity.data_categories:
        return RiskAssessment(
            risk_assessment_id=assessment_id,
            opportunity_id=opportunity.opportunity_id,
            scope="screening",
            jurisdictions=jurisdictions,
            residual_risk="low",
            gate_status="not_applicable",
            evidence_refs=list(opportunity.evidence_refs),
        )

    categories = {item.lower() for item in opportunity.data_categories}
    risks: list[dict[str, str]] = []
    mitigations: list[dict[str, str]] = []
    requires_legal_review = bool(categories & HIGH_IMPACT_CATEGORIES)

    if opportunity.involves_ai:
        risks.append({
            "category": "transparency",
            "risk": "Decisões ou recomendações automatizadas podem não ser explicáveis.",
            "impact": "medium",
            "likelihood": "unknown",
        })
        mitigations.append({
            "risk_category": "transparency",
            "action": "Definir revisão humana, registro de entradas e explicação mínima da decisão.",
        })
        risks.extend([
            {
                "category": "security",
                "risk": "Entradas, saídas ou credenciais do fluxo automatizado podem ficar expostas.",
                "impact": "medium",
                "likelihood": "unknown",
            },
            {
                "category": "governance",
                "risk": "Responsabilidade, retenção e monitoramento do fluxo ainda precisam ser definidos.",
                "impact": "medium",
                "likelihood": "unknown",
            },
        ])
        mitigations.extend([
            {
                "risk_category": "security",
                "action": "Definir controle de acesso, gestão de segredos, logs mínimos e teste de saída.",
            },
            {
                "risk_category": "governance",
                "action": "Definir proprietário, retenção, monitoramento e procedimento de incidente.",
            },
        ])
        if categories & {"credit", "employment", "children"}:
            risks.append({
                "category": "bias",
                "risk": "A decisão automatizada pode produzir tratamento desigual entre grupos.",
                "impact": "high",
                "likelihood": "unknown",
            })
            mitigations.append({
                "risk_category": "bias",
                "action": "Definir critérios de teste, revisão humana e monitoramento de resultados por grupo.",
            })

    if categories:
        risks.append({
            "category": "privacy",
            "risk": "O fluxo utiliza categorias de dados que exigem finalidade e controle de acesso definidos.",
            "impact": "high" if requires_legal_review else "medium",
            "likelihood": "unknown",
        })
        mitigations.append({
            "risk_category": "privacy",
            "action": "Confirmar finalidade, base legal, minimização, retenção e acesso antes da implementação.",
        })
        if "BR" in jurisdictions:
            risks.append({
                "category": "lgpd",
                "risk": "O uso de dados pessoais deve ser revisado à luz da LGPD e da finalidade declarada.",
                "impact": "high" if requires_legal_review else "medium",
                "likelihood": "unknown",
            })
            mitigations.append({
                "risk_category": "lgpd",
                "action": "Encaminhar finalidade, base legal, direitos do titular e retenção para revisão qualificada.",
            })

    controls_validated = bool(opportunity.risk_controls_validated and opportunity.existing_controls)
    if not opportunity.evidence_refs:
        gate_status = "needs_information"
        residual_risk = "unknown"
    elif requires_legal_review and not controls_validated:
        # High-impact categories cannot be treated as executable before qualified
        # review. A reviewer may later change the gate after validating controls.
        gate_status = "blocked"
        residual_risk = "high"
    elif requires_legal_review:
        gate_status = "approved_with_conditions"
        residual_risk = "medium"
    else:
        gate_status = "approved_with_conditions"
        residual_risk = "high" if requires_legal_review else "medium"

    return RiskAssessment(
        risk_assessment_id=assessment_id,
        opportunity_id=opportunity.opportunity_id,
        scope="screening",
        jurisdictions=jurisdictions,
        risks=risks,
        mitigations=mitigations,
        residual_risk=residual_risk,
        gate_status=gate_status,
        evidence_refs=list(opportunity.evidence_refs),
        requires_legal_review=requires_legal_review,
        existing_controls=list(opportunity.existing_controls),
        controls_validated=controls_validated,
    )


def assess_all(opportunities: list[Opportunity], jurisdictions: list[str]) -> list[RiskAssessment]:
    assessments = [assess_opportunity_risk(item, jurisdictions) for item in opportunities]
    for opportunity, assessment in zip(opportunities, assessments):
        opportunity.risk_assessment_id = assessment.risk_assessment_id
        opportunity.risk_gate = assessment.gate_status
        if assessment.gate_status == "blocked":
            opportunity.priority_tier = "blocked"
        elif opportunity.priority_tier == "blocked":
            opportunity.priority_tier = "unranked"
    return assessments
