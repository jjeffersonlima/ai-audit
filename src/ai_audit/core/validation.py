"""Validation rules shared by the CLI and all audit modules."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .models import AuditCase, AuditResult, ValidationIssue, ValidationReport


def _issue(severity: str, code: str, message: str, path: str = "") -> ValidationIssue:
    return ValidationIssue(severity=severity, code=code, message=message, path=path)


def validate_audit_case(case: AuditCase) -> ValidationReport:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    checks = ["manifest", "evidence_ids", "evidence_paths", "evidence_refs"]

    manifest = case.manifest
    required = {
        "audit_id": manifest.audit_id,
        "client_id": manifest.client_id,
        "client_name": manifest.client_name,
    }
    for field_name, value in required.items():
        if not str(value).strip():
            errors.append(_issue("error", "required_field", f"Campo obrigatório ausente: {field_name}", field_name))

    if not manifest.schema_version:
        errors.append(_issue("error", "schema_version_missing", "schema_version é obrigatório", "manifest.schema_version"))
    if not manifest.jurisdictions:
        errors.append(_issue("error", "jurisdiction_missing", "Ao menos uma jurisdição deve ser declarada", "manifest.jurisdictions"))
    if any(not str(item).strip() for item in manifest.jurisdictions):
        errors.append(_issue("error", "jurisdiction_invalid", "Jurisdições não podem ser vazias", "manifest.jurisdictions"))

    evidence_ids = [item.evidence_id for item in case.evidence]
    for evidence_id, count in Counter(evidence_ids).items():
        if count > 1:
            errors.append(_issue("error", "duplicate_evidence_id", f"Evidence ID duplicado: {evidence_id}", "evidence"))

    paths = [item.source_path for item in case.evidence]
    for source_path in paths:
        if not source_path or Path(source_path).is_absolute():
            errors.append(_issue("error", "invalid_evidence_path", "Caminho de evidência deve ser relativo", source_path))

    known_ids = set(evidence_ids)
    for index, item in enumerate(case.evidence):
        if item.metadata.get("json_valid") is False:
            errors.append(_issue("error", "invalid_json", "Arquivo JSON inválido", f"evidence[{index}]"))
        if item.metadata.get("csv_valid") is False:
            errors.append(_issue("error", "invalid_csv", "Arquivo CSV inválido", f"evidence[{index}]"))

    for index, process in enumerate(case.processes):
        evidence_refs = process.evidence_refs if hasattr(process, "evidence_refs") else process.get("evidence_refs", [])
        for evidence_ref in evidence_refs:
            if evidence_ref not in known_ids:
                errors.append(_issue("error", "unknown_evidence_ref", f"Evidência não encontrada: {evidence_ref}", f"processes[{index}].evidence_refs"))

    if not case.evidence:
        warnings.append(_issue("warning", "no_evidence", "Nenhuma evidência foi ingerida", "evidence"))
    if case.pending_questions:
        warnings.append(_issue("warning", "pending_questions", "Existem perguntas pendentes", "pending_questions"))

    return ValidationReport(valid=not errors, errors=errors, warnings=warnings, checks=checks)


def validate_audit_result(result: AuditResult) -> ValidationReport:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    checks = ["result_ids", "opportunity_evidence", "risk_links", "blocked_roadmap"]

    if not str(result.audit_id or "").strip():
        errors.append(_issue("error", "required_field", "audit_id é obrigatório", "audit_id"))
    if not str(result.source_snapshot_hash or "").strip():
        errors.append(_issue("error", "required_field", "source_snapshot_hash é obrigatório", "source_snapshot_hash"))
    if not str(result.schema_version or "").strip():
        errors.append(_issue("error", "schema_version_missing", "schema_version é obrigatório", "schema_version"))

    opportunity_ids = [item.opportunity_id for item in result.opportunities]
    for opportunity_id, count in Counter(opportunity_ids).items():
        if count > 1:
            errors.append(_issue("error", "duplicate_opportunity_id", f"Opportunity ID duplicado: {opportunity_id}", "opportunities"))

    known_evidence_ids = set(result.evidence_ids)
    if result.jurisdictions and any(not str(item).strip() for item in result.jurisdictions):
        errors.append(_issue("error", "jurisdiction_invalid", "Jurisdições do resultado não podem ser vazias", "jurisdictions"))
    referenced_evidence_ids = {ref for item in result.findings for ref in item.evidence_refs}
    referenced_evidence_ids.update(ref for item in result.opportunities for ref in item.evidence_refs)
    referenced_evidence_ids.update(ref for item in result.risk_assessments for ref in item.evidence_refs)
    if not known_evidence_ids and referenced_evidence_ids:
        warnings.append(_issue("warning", "ungrounded_result", "Existem resultados sem referências de evidência", "result"))
    for ref in sorted(referenced_evidence_ids - known_evidence_ids):
        errors.append(_issue("error", "unknown_evidence_ref", f"Evidência não encontrada no snapshot: {ref}", "result"))

    risk_by_id = {item.risk_assessment_id: item for item in result.risk_assessments}
    opportunity_by_id = {item.opportunity_id: item for item in result.opportunities}
    process_by_id = {item.process_id: item for item in result.processes}
    for index, process in enumerate(result.processes):
        if not process.process_id.strip() or not process.name.strip():
            errors.append(_issue("error", "invalid_process", "Processo deve possuir ID e nome", f"processes[{index}]"))
        if not process.evidence_refs:
            errors.append(_issue("error", "process_without_evidence", "Processo sem evidência", f"processes[{index}]"))
        for ref in process.evidence_refs:
            if ref not in known_evidence_ids:
                errors.append(_issue("error", "unknown_evidence_ref", f"Evidência não encontrada no snapshot: {ref}", f"processes[{index}].evidence_refs"))
        for step_index, step in enumerate(process.steps):
            for ref in step.evidence_refs:
                if ref not in known_evidence_ids:
                    errors.append(_issue("error", "unknown_evidence_ref", f"Evidência não encontrada no snapshot: {ref}", f"processes[{index}].steps[{step_index}].evidence_refs"))
    for index, opportunity in enumerate(result.opportunities):
        if not opportunity.evidence_refs:
            errors.append(_issue("error", "opportunity_without_evidence", "Oportunidade sem evidência", f"opportunities[{index}]"))
        if opportunity.risk_assessment_id and opportunity.risk_assessment_id not in risk_by_id:
            errors.append(_issue("error", "unknown_risk_assessment", f"Avaliação de risco não encontrada: {opportunity.risk_assessment_id}", f"opportunities[{index}].risk_assessment_id"))
        if opportunity.risk_gate == "blocked" and opportunity.priority_tier not in {"blocked", "unranked"}:
            errors.append(_issue("error", "blocked_opportunity_ranked", "Oportunidade bloqueada não pode ser priorizada", f"opportunities[{index}]"))
        for process_ref in opportunity.process_refs:
            if process_ref not in process_by_id:
                errors.append(_issue("error", "unknown_process", f"Processo não encontrado: {process_ref}", f"opportunities[{index}].process_refs"))

    for index, finding in enumerate(result.findings):
        if not finding.evidence_refs:
            errors.append(_issue("error", "finding_without_evidence", "Finding sem evidência", f"findings[{index}]"))

    for index, risk in enumerate(result.risk_assessments):
        if risk.opportunity_id and risk.opportunity_id not in opportunity_by_id:
            errors.append(_issue("error", "unknown_opportunity", f"Oportunidade não encontrada: {risk.opportunity_id}", f"risk_assessments[{index}].opportunity_id"))
        if risk.gate_status == "approved" and risk.residual_risk == "unknown":
            errors.append(_issue("error", "approved_unknown_risk", "Risco aprovado sem risco residual conhecido", f"risk_assessments[{index}]"))
        if risk.opportunity_id and not risk.evidence_refs:
            errors.append(_issue("error", "risk_without_evidence", "Avaliação de risco vinculada sem evidência", f"risk_assessments[{index}]"))
        if result.jurisdictions and any(item not in result.jurisdictions for item in risk.jurisdictions):
            errors.append(_issue("error", "undeclared_jurisdiction", "Avaliação usa jurisdição não declarada no resultado", f"risk_assessments[{index}].jurisdictions"))

    return ValidationReport(valid=not errors, errors=errors, warnings=warnings, checks=checks)


def require_valid(report: ValidationReport) -> None:
    if not report.valid:
        messages = "; ".join(item.message for item in report.errors)
        raise ValueError(f"Validação falhou: {messages}")
