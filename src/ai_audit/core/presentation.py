"""Deterministic adapter from AuditResult to the 15-slide presentation schema."""

from __future__ import annotations

from typing import Any

from .models import AuditResult


MISSING = "Dados pendentes"


def _text(value: Any, default: str = MISSING) -> str:
    if value is None or value == "":
        return default
    return str(value)


def _finding_detail(result: AuditResult, index: int) -> dict[str, Any]:
    finding = result.findings[index] if index < len(result.findings) else None
    if finding is None:
        return {
            "section_label": f"DESCOBERTA 0{index + 1}",
            "title": MISSING,
            "metrics": [],
            "quote": {},
            "callout": "Nenhuma descoberta validada foi fornecida para esta seção.",
        }
    return {
        "section_label": f"DESCOBERTA 0{index + 1}",
        "title": finding.title,
        "metrics": [
            {"value": _text(finding.business_impact.get("hours_per_week")), "label": "Horas/semana", "sublabel": "impacto informado"},
            {"value": finding.confidence_level, "label": "Confiança", "sublabel": "classificação"},
        ],
        "quote": {},
        "callout": finding.description,
    }


def audit_result_to_presentation_data(result: AuditResult) -> dict[str, Any]:
    """Build a complete structural payload without inventing business facts."""
    findings = result.findings[:3]
    while len(findings) < 3:
        findings.append(None)

    discoveries = []
    for index, finding in enumerate(findings, start=1):
        discoveries.append({
            "number": f"0{index}",
            "title": finding.title if finding else MISSING,
            "subtitle": "Finding validado" if finding else "Informação necessária",
            "bullets": ([finding.description] if finding else ["Nenhuma evidência suficiente nesta seção."]),
            "color": "amber" if finding else "blue",
        })

    priorities = []
    for index in range(5):
        opportunity = result.opportunities[index] if index < len(result.opportunities) else None
        scenario = opportunity.roi_scenarios[0] if opportunity and opportunity.roi_scenarios else None
        priorities.append({
            "number": f"P{index + 1}",
            "name": opportunity.title if opportunity else MISSING,
            "roi": scenario.first_year_roi if scenario else "—",
            "payback": f"{scenario.monthly_breakeven} mês(es)" if scenario and scenario.monthly_breakeven is not None else "—",
            "timeline": opportunity.timeline if opportunity else "—",
            "phase": opportunity.risk_gate if opportunity else "Não preenchida",
            "color": "green" if opportunity and opportunity.risk_gate in {"not_applicable", "approved"} else "amber",
        })

    quick_wins = []
    transformation = []
    for index, opportunity in enumerate(result.opportunities[:5]):
        item = {
            "priority": f"P{index + 1}",
            "title": opportunity.title,
            "problem": opportunity.problem,
            "solution": opportunity.proposed_solution,
            "tools": MISSING,
            "investment": MISSING,
            "expected_result": MISSING,
            "timeline": opportunity.timeline,
        }
        (quick_wins if index < 2 else transformation).append(item)
    while len(quick_wins) < 2:
        quick_wins.append({"priority": f"P{len(quick_wins) + 1}", "title": MISSING})
    while len(transformation) < 3:
        transformation.append({"priority": f"P{len(transformation) + 3}", "title": MISSING})

    data = {
        "client_name": result.client_name or result.audit_id,
        "metadata": {
            "audit_id": result.audit_id,
            "schema_version": result.schema_version,
            "generator_version": result.generator_version,
            "source_snapshot_hash": result.source_snapshot_hash,
            "approval_status": result.approval.get("status", "draft"),
        },
        "agenda": {
            "block_1": {"time": "0–5 min", "title": "Contexto", "description": "Escopo e evidências recebidas."},
            "block_2": {"time": "5–12 min", "title": "Diagnóstico", "description": "Findings validados."},
            "block_3": {"time": "12–22 min", "title": "Oportunidades", "description": "Prioridades e riscos."},
            "block_4": {"time": "22–30 min", "title": "Próximos passos", "description": "Decisões e ações aprovadas."},
        },
        "diagnostico_kpis": [
            {"value": str(len(result.findings)), "label": "Findings", "description": "Findings validados no AuditResult.", "color": "blue"},
            {"value": str(len(result.opportunities)), "label": "Oportunidades", "description": "Oportunidades com evidências.", "color": "green"},
            {"value": str(len(result.pending_questions)), "label": "Pendências", "description": "Perguntas ainda não resolvidas.", "color": "amber"},
        ],
        "descobertas_criticas": discoveries,
        "descoberta_1_detail": _finding_detail(result, 0),
        "descoberta_2_detail": {"section_label": "DESCOBERTA 02", "title": discoveries[1]["title"], "flow_steps": [], "storage_locations": [], "bottom_stats": []},
        "descoberta_3_detail": {"section_label": "DESCOBERTA 03", "title": discoveries[2]["title"], "funnel_stages": [], "info_panel": {"title": "Evidências", "bullets": discoveries[2]["bullets"]}},
        "custo_status_quo": [{"value": MISSING, "label": "Custo do status quo", "sublabel": "Não calculado sem inputs financeiros."} for _ in range(3)],
        "benchmarks": {"metrics": [MISSING] * 5, "client_values": ["—"] * 5, "market_avg": ["—"] * 5, "top_25": ["—"] * 5, "gap": ["—"] * 5},
        "prioridades": priorities,
        "quick_wins_detail": quick_wins,
        "transformation_detail": transformation,
        "roi_consolidado": {
            "investment": {"value": MISSING, "label": "Investimento Total"},
            "return": {"value": MISSING, "label": "Retorno Estimado"},
            "roi": {"value": MISSING, "label": "ROI"},
            "payback": {"value": MISSING, "label": "Payback Médio"},
        },
        "resultados_esperados": [],
        "proximos_passos": [
            {"number": "1", "title": "Resolver pendências", "description": "Confirmar dados e contradições registradas.", "timeline": "Semana 1"},
            {"number": "2", "title": "Revisar riscos", "description": "Validar gates com os responsáveis.", "timeline": "Semana 2"},
            {"number": "3", "title": "Aprovar execução", "description": "Selecionar oportunidades aprovadas.", "timeline": "Semana 3"},
        ],
    }
    return data


def validate_presentation_data(data: dict[str, Any], *, allow_placeholders: bool = False) -> list[str]:
    errors: list[str] = []
    if not data.get("client_name"):
        errors.append("client_name é obrigatório")
    exact_lengths = {
        "diagnostico_kpis": 3,
        "descobertas_criticas": 3,
        "custo_status_quo": 3,
        "benchmarks.metrics": 5,
        "prioridades": 5,
        "quick_wins_detail": 2,
        "transformation_detail": 3,
        "proximos_passos": 3,
    }
    for field, expected in exact_lengths.items():
        target = data
        for part in field.split("."):
            target = target.get(part, []) if isinstance(target, dict) else []
        if len(target) != expected:
            errors.append(f"{field} deve possuir exatamente {expected} itens")
    if not allow_placeholders:
        def contains_placeholder(value: Any) -> bool:
            if isinstance(value, str):
                return value in {MISSING, "—"}
            if isinstance(value, dict):
                return any(contains_placeholder(item) for item in value.values())
            if isinstance(value, list):
                return any(contains_placeholder(item) for item in value)
            return False

        if contains_placeholder(data):
            errors.append("dados da apresentação ainda contêm placeholders; use --draft ou complete o AuditResult")
    return errors
