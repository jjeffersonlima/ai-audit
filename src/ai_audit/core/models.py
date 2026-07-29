"""Canonical data contracts for the audit pipeline.

The standard library dataclasses are intentionally used in the first slice so
the foundation can be tested without adding a runtime dependency. The public
JSON shape is versioned and can later be generated from a validation library.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from decimal import Decimal
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.2.0"
GENERATOR_VERSION = "0.2.0"


def to_dict(value: Any) -> Any:
    """Convert domain objects into JSON-compatible values."""
    if is_dataclass(value):
        return {key: to_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_dict(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    return value


def dumps_json(value: Any) -> str:
    """Serialize a contract deterministically for reproducible artifacts."""
    return json.dumps(
        to_dict(value),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def write_json(path: str | Path, value: Any) -> Path:
    """Write a UTF-8 contract with stable key ordering."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dumps_json(value), encoding="utf-8")
    return target


def audit_result_from_dict(data: dict[str, Any]) -> "AuditResult":
    """Rehydrate the JSON contract without relying on a third-party mapper."""
    opportunities = []
    for item in data.get("opportunities", []):
        opportunity = dict(item)
        opportunity["roi_scenarios"] = [RoiScenario(**scenario) for scenario in opportunity.get("roi_scenarios", [])]
        opportunities.append(Opportunity(**opportunity))
    processes = []
    for item in data.get("processes", []):
        process = dict(item)
        process["steps"] = [ProcessStep(**step) for step in process.get("steps", [])]
        processes.append(ProcessModel(**process))
    validation_data = data.get("validation_report")
    validation = None
    if validation_data:
        validation = ValidationReport(
            valid=validation_data.get("valid", False),
            errors=[ValidationIssue(**item) for item in validation_data.get("errors", [])],
            warnings=[ValidationIssue(**item) for item in validation_data.get("warnings", [])],
            checks=validation_data.get("checks", []),
        )
    return AuditResult(
        audit_id=data.get("audit_id", ""),
        source_snapshot_hash=data.get("source_snapshot_hash", ""),
        generator_version=data.get("generator_version", ""),
        schema_version=data.get("schema_version", SCHEMA_VERSION),
        client_name=data.get("client_name", ""),
        generated_at=data.get("generated_at", ""),
        evidence_ids=data.get("evidence_ids", []),
        jurisdictions=data.get("jurisdictions", []),
        processes=processes,
        findings=[Finding(**item) for item in data.get("findings", [])],
        opportunities=opportunities,
        risk_assessments=[RiskAssessment(**item) for item in data.get("risk_assessments", [])],
        roadmap=data.get("roadmap", []),
        financial_summary=data.get("financial_summary", {}),
        pending_questions=data.get("pending_questions", []),
        contradictions=data.get("contradictions", []),
        assumptions=data.get("assumptions", []),
        validation_report=validation,
        approval=data.get("approval", {"status": "draft"}),
    )


@dataclass
class AuditManifest:
    audit_id: str
    client_id: str
    client_name: str
    locale: str = "pt-BR"
    jurisdictions: list[str] = field(default_factory=lambda: ["BR"])
    audit_scope: list[str] = field(
        default_factory=lambda: ["opportunity_audit", "risk_assessment"]
    )
    schema_version: str = SCHEMA_VERSION
    created_at: str = ""
    updated_at: str = ""
    data_retention: str = "manual_review_required"
    approval_status: str = "draft"
    approved_by: str | None = None


@dataclass
class EvidenceItem:
    evidence_id: str
    source_type: str
    source_path: str
    content_hash: str
    content: str
    language: str = "unknown"
    sensitivity: str = "unknown"
    contains_personal_data: bool = False
    collected_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessStep:
    step_id: str
    name: str
    owner: str = ""
    tools: list[str] = field(default_factory=list)
    frequency: str = ""
    volume: str = ""
    duration_minutes: str | None = None
    handoff_to: str = ""
    evidence_refs: list[str] = field(default_factory=list)


@dataclass
class ProcessModel:
    process_id: str
    name: str
    objective: str = ""
    steps: list[ProcessStep] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    status: str = "draft"


@dataclass
class AuditCase:
    manifest: AuditManifest
    evidence: list[EvidenceItem] = field(default_factory=list)
    profile: dict[str, Any] = field(default_factory=dict)
    questionnaire: dict[str, Any] = field(default_factory=dict)
    processes: list[ProcessModel] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    pending_questions: list[str] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Finding:
    finding_id: str
    module: str
    kind: str
    title: str
    description: str
    evidence_refs: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    confidence_level: str = "low"
    confidence_rationale: str = ""
    business_impact: dict[str, Any] = field(default_factory=dict)
    status: str = "draft"


@dataclass
class RoiScenario:
    name: str
    annual_manual_cost: str
    annual_automated_cost: str
    first_year_investment: str
    annual_savings: str
    first_year_roi: str | None
    monthly_breakeven: int | None
    three_year_savings: str
    assumptions: list[str] = field(default_factory=list)
    formula_version: str = "roi-v1"
    inputs: dict[str, str] = field(default_factory=dict)


@dataclass
class Opportunity:
    opportunity_id: str
    title: str
    problem: str
    proposed_solution: str
    evidence_refs: list[str] = field(default_factory=list)
    process_refs: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    implementation_effort: str = "unknown"
    timeline: str = "unknown"
    roi_scenarios: list[RoiScenario] = field(default_factory=list)
    risk_assessment_id: str | None = None
    risk_gate: str = "needs_information"
    priority_dimensions: dict[str, Any] = field(default_factory=dict)
    priority_tier: str = "unranked"
    involves_ai: bool = False
    data_categories: list[str] = field(default_factory=list)
    existing_controls: list[str] = field(default_factory=list)
    risk_controls_validated: bool = False
    status: str = "draft"


@dataclass
class RiskAssessment:
    risk_assessment_id: str
    opportunity_id: str | None
    scope: str
    jurisdictions: list[str]
    risks: list[dict[str, Any]] = field(default_factory=list)
    existing_controls: list[str] = field(default_factory=list)
    mitigations: list[dict[str, Any]] = field(default_factory=list)
    residual_risk: str = "unknown"
    gate_status: str = "needs_information"
    evidence_refs: list[str] = field(default_factory=list)
    requires_legal_review: bool = False
    controls_validated: bool = False


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    path: str = ""


@dataclass
class ValidationReport:
    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return to_dict(self)


@dataclass
class AuditResult:
    audit_id: str
    source_snapshot_hash: str
    generator_version: str
    schema_version: str = SCHEMA_VERSION
    client_name: str = ""
    generated_at: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    jurisdictions: list[str] = field(default_factory=list)
    processes: list[ProcessModel] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    risk_assessments: list[RiskAssessment] = field(default_factory=list)
    roadmap: list[str] = field(default_factory=list)
    financial_summary: dict[str, Any] = field(default_factory=dict)
    pending_questions: list[str] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    validation_report: ValidationReport | None = None
    approval: dict[str, Any] = field(default_factory=lambda: {"status": "draft"})

    def to_dict(self) -> dict[str, Any]:
        return to_dict(self)
