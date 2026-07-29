"""Deterministic ingestion and evidence indexing."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AuditCase, AuditManifest, EvidenceItem, write_json
from .validation import validate_audit_case


SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".csv"}
PII_PATTERNS = (
    re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b"),
    re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}\b"),
    re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _language(text: str) -> str:
    portuguese_markers = ("ção", "ções", "não", "para", "você", "empresa", "processo")
    return "pt-BR" if any(marker in text.lower() for marker in portuguese_markers) else "unknown"


def _source_type(relative_path: Path) -> str:
    normalized = "/".join(relative_path.parts).lower()
    if "transcript" in normalized or "call" in normalized:
        return "transcript"
    if "questionnaire" in normalized or "onboarding" in normalized:
        return "questionnaire"
    if "profile" in normalized or "context" in normalized:
        return "client_profile"
    if "process" in normalized:
        return "process_documentation"
    return relative_path.suffix.lstrip(".") or "unknown"


def _parse_metadata(path: Path, content: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"extension": path.suffix.lower()}
    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(content)
            metadata["json_valid"] = True
            metadata["json_type"] = type(parsed).__name__
        except json.JSONDecodeError as exc:
            metadata["json_valid"] = False
            metadata["parse_error"] = str(exc)
    elif path.suffix.lower() == ".csv":
        try:
            rows = list(csv.reader(content.splitlines()))
            metadata["csv_valid"] = True
            metadata["row_count"] = len(rows)
            metadata["column_count"] = len(rows[0]) if rows else 0
        except csv.Error as exc:
            metadata["csv_valid"] = False
            metadata["parse_error"] = str(exc)
    return metadata


def _parse_labeled_markdown(content: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(r"^\s*(?:\d+\.\s*)?([^:\n]+?)\s*:\s*(.*?)\s*$")
    for line in content.splitlines():
        match = pattern.match(line.replace("**", ""))
        if match and match.group(2):
            key = re.sub(r"[^a-z0-9]+", "_", match.group(1).strip().lower()).strip("_")
            if key:
                values[key] = match.group(2).strip()
    return values


def _normalize_structured_content(item: EvidenceItem) -> dict[str, Any]:
    if item.source_type not in {"client_profile", "questionnaire"}:
        return {}
    if item.metadata.get("json_valid") is True:
        parsed = json.loads(item.content)
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    if item.metadata.get("csv_valid") is True:
        rows = list(csv.DictReader(item.content.splitlines()))
        return {"rows": rows}
    if item.source_type in {"client_profile", "questionnaire"}:
        return _parse_labeled_markdown(item.content)
    return {}


def ingest_workspace(workspace: str | Path) -> AuditCase:
    root = Path(workspace).resolve()
    manifest_path = root / "working" / "audit_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifesto não encontrado: {manifest_path}")

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = AuditManifest(**manifest_data)
    input_root = root / "input"
    evidence: list[EvidenceItem] = []
    evidence_by_hash: dict[str, EvidenceItem] = {}

    if input_root.exists():
        for path in sorted(input_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            raw = path.read_bytes()
            content = raw.decode("utf-8", errors="replace")
            relative_path = path.relative_to(input_root)
            digest = hashlib.sha256(raw).hexdigest()
            if digest in evidence_by_hash:
                duplicate = evidence_by_hash[digest]
                duplicate.metadata.setdefault("duplicate_sources", []).append(relative_path.as_posix())
                continue
            evidence_id = f"E-{digest[:12]}"
            contains_pii = any(pattern.search(content) for pattern in PII_PATTERNS)
            item = EvidenceItem(
                evidence_id=evidence_id,
                source_type=_source_type(relative_path),
                source_path=relative_path.as_posix(),
                content_hash=digest,
                content=content,
                language=_language(content),
                sensitivity="personal_data" if contains_pii else "internal",
                contains_personal_data=contains_pii,
                collected_at=utc_now(),
                metadata=_parse_metadata(path, content),
            )
            evidence.append(item)
            evidence_by_hash[digest] = item

    profile: dict[str, Any] = {}
    questionnaire: dict[str, Any] = {}
    for item in evidence:
        normalized = _normalize_structured_content(item)
        if item.source_type == "client_profile":
            profile.update(normalized)
        elif item.source_type == "questionnaire":
            questionnaire.update(normalized)

    pending_questions: list[str] = []
    if not profile:
        pending_questions.append("Perfil da empresa não foi identificado ou está vazio.")
    if not questionnaire:
        pending_questions.append("Questionário de onboarding não foi identificado ou está vazio.")

    case = AuditCase(
        manifest=manifest,
        evidence=evidence,
        profile=profile,
        questionnaire=questionnaire,
        pending_questions=pending_questions,
    )
    report = validate_audit_case(case)
    (root / "working").mkdir(parents=True, exist_ok=True)
    write_json(root / "working" / "evidence_index.json", {
        "schema_version": manifest.schema_version,
        "evidence": evidence,
    })
    write_json(root / "working" / "audit_case.json", {
        **case.__dict__,
        "validation_report": report.to_dict(),
    })
    return case
