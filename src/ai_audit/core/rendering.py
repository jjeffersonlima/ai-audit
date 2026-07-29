"""Render validated audit results into human-readable deliverables."""

from __future__ import annotations

import csv
import io

from .models import AuditResult
from .validation import require_valid, validate_audit_result


def render_markdown(result: AuditResult) -> str:
    report = [
        f"# AI Audit — {result.client_name or result.audit_id}",
        "",
        f"- Gerado em: {result.generated_at or 'não registrado'}",
        f"- Schema: {result.schema_version}",
        f"- Versão do gerador: {result.generator_version}",
        f"- Snapshot de fontes: `{result.source_snapshot_hash}`",
        f"- Status: {result.approval.get('status', 'draft')}",
        "",
        "## Resumo executivo",
        "",
        f"- Findings: {len(result.findings)}",
        f"- Oportunidades: {len(result.opportunities)}",
        f"- Avaliações de risco: {len(result.risk_assessments)}",
        f"- Perguntas pendentes: {len(result.pending_questions)}",
        "",
        "## Findings",
        "",
    ]
    if result.findings:
        for finding in result.findings:
            refs = ", ".join(finding.evidence_refs) or "sem evidência"
            report.extend([
                f"### {finding.finding_id} — {finding.title}",
                "",
                finding.description,
                "",
                f"- Tipo: {finding.kind}",
                f"- Confiança: {finding.confidence_level} — {finding.confidence_rationale}",
                f"- Evidências: {refs}",
                "",
            ])
    else:
        report.extend(["Nenhum finding validado.", ""])

    report.extend(["## Oportunidades", "", "| ID | Oportunidade | Gate de risco | Prioridade | ROI base | Evidências |", "|---|---|---|---|---|---|"])
    for opportunity in result.opportunities:
        base_scenario = next((item for item in opportunity.roi_scenarios if item.name == "base"), None)
        report.append(
            f"| {opportunity.opportunity_id} | {opportunity.title} | {opportunity.risk_gate} | "
            f"{opportunity.priority_tier} | {base_scenario.first_year_roi if base_scenario else '—'} | "
            f"{', '.join(opportunity.evidence_refs)} |"
        )
    if not result.opportunities:
        report.append("| — | Nenhuma oportunidade validada | — | — | — | — |")
    report.append("")

    report.extend(["## Avaliação de riscos", ""])
    for risk in result.risk_assessments:
        report.extend([
            f"### {risk.risk_assessment_id}",
            "",
            f"- Oportunidade: {risk.opportunity_id or 'transversal'}",
            f"- Gate: {risk.gate_status}",
            f"- Risco residual: {risk.residual_risk}",
            f"- Revisão jurídica necessária: {'sim' if risk.requires_legal_review else 'não'}",
            "",
        ])

    report.extend(["## Perguntas pendentes", ""])
    if result.pending_questions:
        report.extend(f"- {question}" for question in result.pending_questions)
    else:
        report.append("Nenhuma pergunta pendente.")
    report.append("")

    if result.assumptions:
        report.extend(["## Assumptions", ""])
        report.extend(f"- {assumption}" for assumption in result.assumptions)
        report.append("")

    return "\n".join(report)


def render_scoring_matrix(result: AuditResult) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow([
        "Audit ID", "Schema Version", "Generator Version", "Source Snapshot Hash",
        "Category", "Criteria", "Score", "Notes",
    ])
    for opportunity in result.opportunities:
        dimensions = opportunity.priority_dimensions
        writer.writerow([
            result.audit_id,
            result.schema_version,
            result.generator_version,
            result.source_snapshot_hash,
            "Opportunity",
            opportunity.title,
            dimensions.get("value", ""),
            f"gate={opportunity.risk_gate}; priority={opportunity.priority_tier}; "
            f"roi_base={next((item.first_year_roi for item in opportunity.roi_scenarios if item.name == 'base'), '—')}",
        ])
    for risk in result.risk_assessments:
        writer.writerow([
            result.audit_id,
            result.schema_version,
            result.generator_version,
            result.source_snapshot_hash,
            "Risk",
            risk.risk_assessment_id,
            risk.residual_risk,
            f"gate={risk.gate_status}",
        ])
    return output.getvalue()


def render_opportunity_report(result: AuditResult) -> str:
    """Render the opportunity module without re-reading another output."""
    report = [
        f"# Opportunity Audit — {result.client_name or result.audit_id}",
        "",
        f"- Audit ID: `{result.audit_id}`",
        f"- Snapshot: `{result.source_snapshot_hash}`",
        f"- Status: {result.approval.get('status', 'draft')}",
        "",
        "## Findings",
        "",
    ]
    for finding in result.findings:
        report.extend([
            f"### {finding.finding_id} — {finding.title}",
            "",
            finding.description,
            "",
            f"- Evidências: {', '.join(finding.evidence_refs) or 'pendente'}",
            f"- Confiança: {finding.confidence_level}",
            "",
        ])
    if not result.findings:
        report.append("Nenhum finding validado.")
        report.append("")

    report.extend(["## Oportunidades", ""])
    for opportunity in result.opportunities:
        report.extend([
            f"### {opportunity.opportunity_id} — {opportunity.title}",
            "",
            f"- Problema: {opportunity.problem}",
            f"- Solução: {opportunity.proposed_solution}",
            f"- Gate de risco: {opportunity.risk_gate}",
            f"- Prioridade: {opportunity.priority_tier}",
            f"- Evidências: {', '.join(opportunity.evidence_refs)}",
        ])
        if opportunity.process_refs:
            report.append(f"- Processos: {', '.join(opportunity.process_refs)}")
        if opportunity.roi_scenarios:
            report.append("")
            report.append("#### ROI informado e calculado")
            report.append("")
            report.extend(
                f"- {scenario.name}: ROI {scenario.first_year_roi or 'não calculável'}; "
                f"payback {scenario.monthly_breakeven if scenario.monthly_breakeven is not None else 'não calculável'} mês(es); "
                f"fórmula `{scenario.formula_version}`"
                for scenario in opportunity.roi_scenarios
            )
        report.append("")
    if not result.opportunities:
        report.append("Nenhuma oportunidade validada.")
        report.append("")
    return "\n".join(report)


def render_risk_report(result: AuditResult) -> str:
    """Render the risk module and its gates from the canonical result."""
    report = [
        f"# Risk Assessment — {result.client_name or result.audit_id}",
        "",
        f"- Audit ID: `{result.audit_id}`",
        f"- Jurisdições declaradas: {', '.join(result.jurisdictions) or 'não informadas'}",
        f"- Snapshot: `{result.source_snapshot_hash}`",
        "",
    ]
    if not result.risk_assessments:
        report.extend(["Nenhuma avaliação de risco registrada.", ""])
    for risk in result.risk_assessments:
        report.extend([
            f"## {risk.risk_assessment_id}",
            "",
            f"- Oportunidade: {risk.opportunity_id or 'transversal'}",
            f"- Gate: {risk.gate_status}",
            f"- Risco residual: {risk.residual_risk}",
            f"- Revisão qualificada necessária: {'sim' if risk.requires_legal_review else 'não'}",
            f"- Controles validados: {'sim' if risk.controls_validated else 'não'}",
            f"- Evidências: {', '.join(risk.evidence_refs) or 'pendente'}",
            "",
        ])
        if risk.risks:
            report.append("### Riscos")
            report.append("")
            report.extend(f"- {item.get('category', 'unknown')}: {item.get('risk', '')}" for item in risk.risks)
            report.append("")
        if risk.mitigations:
            report.append("### Mitigações")
            report.append("")
            report.extend(f"- {item.get('action', '')}" for item in risk.mitigations)
            report.append("")
    return "\n".join(report)


def render_deliverables(result: AuditResult, output_dir: str, *, draft: bool = False) -> list[str]:
    report = validate_audit_result(result)
    if not draft:
        require_valid(report)
        if result.approval.get("status") not in {"approved", "approved_with_conditions"}:
            raise ValueError("AuditResult ainda não foi aprovado; use --draft para gerar rascunho")

    from pathlib import Path

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    report_path = root / "Final Audit Report.md"
    opportunity_path = root / "Opportunity Audit Report.md"
    risk_path = root / "Risk Assessment Report.md"
    matrix_path = root / "VALUE Scoring Matrix.csv"
    report_path.write_text(render_markdown(result), encoding="utf-8")
    opportunity_path.write_text(render_opportunity_report(result), encoding="utf-8")
    risk_path.write_text(render_risk_report(result), encoding="utf-8")
    matrix_path.write_text(render_scoring_matrix(result), encoding="utf-8")
    return [str(report_path), str(opportunity_path), str(risk_path), str(matrix_path)]
