"""Opportunity analysis primitives.

This module deliberately does not pretend to infer business facts from raw
text. An agent may propose normalized process candidates, but this module
validates their shape and creates traceable domain objects.
"""

from __future__ import annotations

import hashlib
from typing import Any

from ..core.calculations import RoiInputs, calculate_roi_scenarios
from ..core.models import AuditCase, AuditResult, Finding, Opportunity, ProcessModel, ProcessStep, GENERATOR_VERSION


def _strict_bool(value: Any, field_name: str, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "sim", "yes"}:
            return True
        if normalized in {"false", "0", "não", "nao", "no"}:
            return False
    raise ValueError(f"{field_name} deve ser booleano")


def _process_from_candidate(candidate: dict[str, Any], index: int) -> ProcessModel | None:
    raw = candidate.get("process")
    if not isinstance(raw, dict):
        return None
    process_id = str(raw.get("process_id") or (candidate.get("process_refs") or [f"process-{index:03d}"])[0])
    raw_steps = raw.get("steps", [])
    if not isinstance(raw_steps, list):
        return None
    steps: list[ProcessStep] = []
    for step_index, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict) or not str(raw_step.get("name", "")).strip():
            continue
        duration = raw_step.get("duration_minutes")
        steps.append(ProcessStep(
            step_id=str(raw_step.get("step_id") or f"{process_id}-step-{step_index:02d}"),
            name=str(raw_step["name"]),
            owner=str(raw_step.get("owner", "")),
            tools=[str(item) for item in raw_step.get("tools", [])],
            frequency=str(raw_step.get("frequency", "")),
            volume=str(raw_step.get("volume", "")),
            duration_minutes=None if duration in (None, "") else str(duration),
            handoff_to=str(raw_step.get("handoff_to", "")),
            evidence_refs=[str(item) for item in raw_step.get("evidence_refs", candidate.get("evidence_refs", []))],
        ))
    return ProcessModel(
        process_id=process_id,
        name=str(raw.get("name") or candidate.get("title", process_id)),
        objective=str(raw.get("objective", "")),
        steps=steps,
        evidence_refs=[str(item) for item in raw.get("evidence_refs", candidate.get("evidence_refs", []))],
        status="validated" if steps else "draft",
    )


def _roi_scenarios(candidate: dict[str, Any]) -> tuple[list[Any], str | None]:
    raw = candidate.get("roi_inputs")
    if raw is None:
        return [], None
    if not isinstance(raw, dict):
        return [], "roi_inputs deve ser um objeto com cenários explícitos"
    if all(name in raw for name in ("hours_per_execution", "executions_per_month", "hourly_cost", "error_rate", "cost_per_error")):
        raw = {"base": raw}
    try:
        scenarios = {name: RoiInputs.from_mapping(values) for name, values in raw.items() if isinstance(values, dict)}
        if not scenarios:
            return [], "roi_inputs não contém cenários válidos"
        return calculate_roi_scenarios(scenarios), None
    except (TypeError, ValueError) as exc:
        return [], str(exc)


def analyze_opportunities(case: AuditCase, candidates: list[dict[str, Any]]) -> tuple[list[Finding], list[Opportunity], list[str]]:
    known_evidence = {item.evidence_id for item in case.evidence}
    findings: list[Finding] = []
    opportunities: list[Opportunity] = []
    pending: list[str] = []

    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            pending.append(f"Candidato {index}: o item deve ser um objeto JSON")
            continue
        title = str(candidate.get("title", "")).strip()
        raw_evidence_refs = candidate.get("evidence_refs", [])
        if not isinstance(raw_evidence_refs, list):
            pending.append(f"{title or f'Candidato {index}'}: evidence_refs deve ser uma lista")
            continue
        evidence_refs = [str(ref).strip() for ref in raw_evidence_refs if str(ref).strip()]
        missing_refs = [ref for ref in evidence_refs if ref not in known_evidence]
        if not title:
            pending.append(f"Candidato {index}: título da oportunidade ausente")
            continue
        if not str(candidate.get("problem", "")).strip():
            pending.append(f"{title}: problema não descrito")
            continue
        if not str(candidate.get("proposed_solution", "")).strip():
            pending.append(f"{title}: solução proposta não descrita")
            continue
        if not evidence_refs:
            pending.append(f"{title}: pelo menos uma evidência é obrigatória")
            continue
        if missing_refs:
            pending.append(f"{title}: evidências não encontradas: {', '.join(missing_refs)}")
            continue
        roi_scenarios, roi_error = _roi_scenarios(candidate)
        if roi_error:
            pending.append(f"{title}: ROI pendente — {roi_error}")
        try:
            involves_ai = _strict_bool(candidate.get("involves_ai"), "involves_ai")
            risk_controls_validated = _strict_bool(candidate.get("risk_controls_validated"), "risk_controls_validated")
        except ValueError as exc:
            pending.append(f"{title}: {exc}")
            continue
        process = _process_from_candidate(candidate, index)
        if process is not None and all(item.process_id != process.process_id for item in case.processes):
            case.processes.append(process)
        process_refs = [str(ref).strip() for ref in candidate.get("process_refs", []) if str(ref).strip()]
        known_process_ids = {item.process_id for item in case.processes}
        missing_processes = [ref for ref in process_refs if ref not in known_process_ids]
        if missing_processes:
            pending.append(f"{title}: processos não encontrados: {', '.join(missing_processes)}")
            continue
        opportunity_id = str(candidate.get("opportunity_id") or f"OP-{index:03d}")
        finding_id = f"F-{opportunity_id[3:]}" if opportunity_id.startswith("OP-") else f"F-{index:03d}"
        finding = Finding(
            finding_id=finding_id,
            module="opportunity_audit",
            kind="process_bottleneck",
            title=title,
            description=str(candidate.get("problem", "Problema ainda não descrito")),
            evidence_refs=evidence_refs,
            assumptions=[str(item) for item in candidate.get("assumptions", [])],
            confidence_level=str(candidate.get("confidence_level", "medium")),
            confidence_rationale=str(candidate.get("confidence_rationale", "Candidato normalizado a partir de evidências fornecidas.")),
            business_impact=dict(candidate.get("business_impact", {})),
            status="validated",
        )
        opportunity = Opportunity(
            opportunity_id=opportunity_id,
            title=title,
            problem=str(candidate.get("problem", "")),
            proposed_solution=str(candidate.get("proposed_solution", "")),
            evidence_refs=evidence_refs,
            process_refs=process_refs,
            dependencies=[str(item) for item in candidate.get("dependencies", [])],
            implementation_effort=str(candidate.get("implementation_effort", "unknown")),
            timeline=str(candidate.get("timeline", "unknown")),
            roi_scenarios=roi_scenarios,
            priority_dimensions=dict(candidate.get("priority_dimensions", {})),
            priority_tier="unranked",
            involves_ai=involves_ai,
            data_categories=[str(item) for item in candidate.get("data_categories", [])],
            existing_controls=[str(item) for item in candidate.get("existing_controls", [])],
            risk_controls_validated=risk_controls_validated,
            status="validated",
        )
        findings.append(finding)
        opportunities.append(opportunity)

    if not candidates:
        pending.append("Fornecer pelo menos um processo ou candidato de oportunidade para análise.")
    return findings, opportunities, pending


def source_snapshot_hash(case: AuditCase) -> str:
    payload = "\n".join(f"{item.evidence_id}:{item.content_hash}" for item in case.evidence)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_audit_result(case: AuditCase, findings: list[Finding], opportunities: list[Opportunity], risks: list[Any], pending: list[str]) -> AuditResult:
    return AuditResult(
        audit_id=case.manifest.audit_id,
        source_snapshot_hash=source_snapshot_hash(case),
        generator_version=GENERATOR_VERSION,
        schema_version=case.manifest.schema_version,
        client_name=case.manifest.client_name,
        evidence_ids=[item.evidence_id for item in case.evidence],
        jurisdictions=list(case.manifest.jurisdictions),
        processes=list(case.processes),
        findings=findings,
        opportunities=opportunities,
        risk_assessments=risks,
        pending_questions=[*case.pending_questions, *pending],
        contradictions=case.contradictions,
        assumptions=[],
    )
