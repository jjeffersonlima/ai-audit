"""Deterministic quality indicators for an AuditResult."""

from __future__ import annotations

from typing import Any

from .models import AuditResult
from .validation import validate_audit_result


def evaluate_result_quality(result: AuditResult) -> dict[str, Any]:
    """Measure traceability and review readiness without judging business value."""
    material_items = [*result.findings, *result.opportunities, *result.risk_assessments]
    supported_items = [item for item in material_items if getattr(item, "evidence_refs", [])]
    unsupported_items = [
        getattr(item, "finding_id", None)
        or getattr(item, "opportunity_id", None)
        or getattr(item, "risk_assessment_id", None)
        for item in material_items
        if not getattr(item, "evidence_refs", [])
    ]
    validation = validate_audit_result(result)
    pending_count = len(result.pending_questions)
    contradiction_count = len(result.contradictions)
    coverage = 1.0 if not material_items else round(len(supported_items) / len(material_items), 4)
    status = "fail" if not validation.valid else "review" if pending_count or contradiction_count else "pass"
    return {
        "schema_version": result.schema_version,
        "audit_id": result.audit_id,
        "source_snapshot_hash": result.source_snapshot_hash,
        "material_items": len(material_items),
        "supported_items": len(supported_items),
        "unsupported_item_ids": unsupported_items,
        "evidence_coverage": coverage,
        "pending_questions": pending_count,
        "contradictions": contradiction_count,
        "blocked_opportunities": sum(item.risk_gate == "blocked" for item in result.opportunities),
        "validation_errors": len(validation.errors),
        "status": status,
    }
