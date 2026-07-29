"""Command-line entry point for the new audit pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path

from .core.calculations import RoiInputs, calculate_roi
from .core.ingestion import ingest_workspace
from .core.models import audit_result_from_dict, write_json
from .core.rendering import render_deliverables
from .core.quality import evaluate_result_quality
from .core.validation import validate_audit_case, validate_audit_result
from .core.workspace import init_workspace
from .modules.opportunity_audit import analyze_opportunities, build_audit_result
from .modules.risk_assessment import assess_all


def _workspace_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", required=True, help="Diretório do workspace do cliente")


def _decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except Exception as exc:
        raise argparse.ArgumentTypeError(f"Valor decimal inválido: {value}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-audit", description="AI Audit — pipeline baseado em evidências")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Criar workspace de cliente")
    init.add_argument("--client", required=True, help="Nome da empresa")
    init.add_argument("--workspace", required=True, help="Diretório do workspace")
    init.add_argument("--force", action="store_true", help="Permitir workspace existente vazio")

    for name, help_text in (
        ("ingest", "Ingerir arquivos e gerar índice de evidências"),
        ("validate-case", "Validar o AuditCase ingerido"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        _workspace_arg(command)

    analyze = subparsers.add_parser("analyze-opportunities", help="Validar candidatos e gerar AuditResult")
    _workspace_arg(analyze)
    analyze.add_argument("--candidates", help="JSON com candidatos normalizados; padrão: working/opportunity_candidates.json")

    risks = subparsers.add_parser("analyze-risks", help="Reavaliar riscos do AuditResult existente")
    _workspace_arg(risks)

    validate_result = subparsers.add_parser("validate-result", help="Validar AuditResult existente")
    _workspace_arg(validate_result)

    quality = subparsers.add_parser("quality", help="Medir rastreabilidade e prontidão do diagnóstico")
    _workspace_arg(quality)

    render = subparsers.add_parser("render", help="Gerar relatórios e matriz a partir do AuditResult")
    _workspace_arg(render)
    render.add_argument("--draft", action="store_true", help="Permitir renderização sem aprovação final")

    approve = subparsers.add_parser("approve", help="Registrar aprovação humana do AuditResult")
    _workspace_arg(approve)
    approve.add_argument("--reviewer", required=True, help="Nome ou identificador do revisor")
    approve.add_argument("--status", choices=["approved", "approved_with_conditions"], default="approved")

    roi = subparsers.add_parser("calculate-roi", help="Calcular ROI de forma determinística")
    roi.add_argument("--output", required=True, help="Arquivo JSON de saída")
    for name in (
        "hours-per-execution", "executions-per-month", "hourly-cost", "error-rate",
        "cost-per-error", "automation-hours-per-execution", "automation-error-rate",
        "monthly-subscription", "setup-hours", "consultant-hourly-rate",
    ):
        roi.add_argument(f"--{name}", type=_decimal, required=name in {"hours-per-execution", "executions-per-month", "hourly-cost", "error-rate", "cost-per-error"}, default=Decimal("0"))

    status = subparsers.add_parser("status", help="Mostrar artefatos do workspace")
    _workspace_arg(status)

    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "init":
        root = init_workspace(args.client, args.workspace, force=args.force)
        print(f"Workspace criado: {root}")
        return 0

    if args.command == "ingest":
        case = ingest_workspace(args.workspace)
        report = validate_audit_case(case)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0 if report.valid else 1

    if args.command == "validate-case":
        case = ingest_workspace(args.workspace)
        report = validate_audit_case(case)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0 if report.valid else 1

    if args.command == "analyze-opportunities":
        root = Path(args.workspace).resolve()
        case = ingest_workspace(root)
        case_report = validate_audit_case(case)
        if not case_report.valid:
            raise ValueError("AuditCase inválido; execute a correção das entradas antes da análise")
        candidate_path = Path(args.candidates) if args.candidates else root / "working" / "opportunity_candidates.json"
        if args.candidates and not candidate_path.is_absolute():
            candidate_path = root / candidate_path
        if not candidate_path.exists():
            raise FileNotFoundError(f"Candidatos não encontrados: {candidate_path}")
        candidates = json.loads(candidate_path.read_text(encoding="utf-8"))
        if not isinstance(candidates, list):
            raise ValueError("Arquivo de candidatos deve conter uma lista JSON")
        findings, opportunities, pending = analyze_opportunities(case, candidates)
        risks = assess_all(opportunities, case.manifest.jurisdictions)
        result = build_audit_result(case, findings, opportunities, risks, pending)
        validation = validate_audit_result(result)
        result.validation_report = validation
        result_path = root / "working" / "audit_result.json"
        write_json(result_path, result)
        print(json.dumps(validation.to_dict(), ensure_ascii=False, indent=2))
        return 0 if validation.valid else 1

    if args.command == "analyze-risks":
        root = Path(args.workspace).resolve()
        result_path = root / "working" / "audit_result.json"
        manifest_path = root / "working" / "audit_manifest.json"
        if not result_path.exists():
            raise FileNotFoundError(f"AuditResult não encontrado: {result_path}")
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifesto não encontrado: {manifest_path}")
        result = audit_result_from_dict(json.loads(result_path.read_text(encoding="utf-8")))
        current_report = validate_audit_result(result)
        if not current_report.valid:
            raise ValueError("AuditResult inválido; corrija a análise de oportunidades antes de reavaliar riscos")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        jurisdictions = [str(item) for item in manifest.get("jurisdictions", [])]
        result.risk_assessments = assess_all(result.opportunities, jurisdictions)
        validation = validate_audit_result(result)
        result.validation_report = validation
        write_json(result_path, result)
        print(json.dumps(validation.to_dict(), ensure_ascii=False, indent=2))
        return 0 if validation.valid else 1

    if args.command == "validate-result":
        result_path = Path(args.workspace).resolve() / "working" / "audit_result.json"
        if not result_path.exists():
            raise FileNotFoundError(f"AuditResult não encontrado: {result_path}")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        result = audit_result_from_dict(data)
        report = validate_audit_result(result)
        validation_path = result_path.parent / "validation_report.json"
        write_json(validation_path, report)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0 if report.valid else 1

    if args.command == "quality":
        result_path = Path(args.workspace).resolve() / "working" / "audit_result.json"
        if not result_path.exists():
            raise FileNotFoundError(f"AuditResult não encontrado: {result_path}")
        result = audit_result_from_dict(json.loads(result_path.read_text(encoding="utf-8")))
        quality_report = evaluate_result_quality(result)
        write_json(result_path.parent / "quality_report.json", quality_report)
        print(json.dumps(quality_report, ensure_ascii=False, indent=2))
        return 0 if quality_report["status"] != "fail" else 1

    if args.command == "render":
        root = Path(args.workspace).resolve()
        result_path = root / "working" / "audit_result.json"
        if not result_path.exists():
            raise FileNotFoundError(f"AuditResult não encontrado: {result_path}")
        result = audit_result_from_dict(json.loads(result_path.read_text(encoding="utf-8")))
        outputs = render_deliverables(result, str(root / "output"), draft=args.draft)
        print(json.dumps({"outputs": outputs, "draft": args.draft}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "approve":
        root = Path(args.workspace).resolve()
        result_path = root / "working" / "audit_result.json"
        if not result_path.exists():
            raise FileNotFoundError(f"AuditResult não encontrado: {result_path}")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        result = audit_result_from_dict(data)
        report = validate_audit_result(result)
        if not report.valid:
            raise ValueError("Não é possível aprovar um AuditResult inválido")
        if args.status == "approved" and result.pending_questions:
            raise ValueError("Existem perguntas pendentes; use approved_with_conditions ou resolva-as")
        result.approval = {
            "status": args.status,
            "reviewer": args.reviewer,
            "approved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }
        write_json(result_path, result)
        print(json.dumps(result.approval, ensure_ascii=False, indent=2))
        return 0

    if args.command == "calculate-roi":
        inputs = RoiInputs(
            hours_per_execution=args.hours_per_execution,
            executions_per_month=args.executions_per_month,
            hourly_cost=args.hourly_cost,
            error_rate=args.error_rate,
            cost_per_error=args.cost_per_error,
            automation_hours_per_execution=args.automation_hours_per_execution,
            automation_error_rate=args.automation_error_rate,
            monthly_subscription=args.monthly_subscription,
            setup_hours=args.setup_hours,
            consultant_hourly_rate=args.consultant_hourly_rate,
        )
        result = calculate_roi(inputs)
        write_json(args.output, result)
        print(f"ROI salvo em: {args.output}")
        return 0

    if args.command == "status":
        root = Path(args.workspace).resolve()
        artifacts = sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())
        print(json.dumps({"workspace": str(root), "artifacts": artifacts}, ensure_ascii=False, indent=2))
        return 0

    return 2


def main() -> None:
    parser = build_parser()
    try:
        raise SystemExit(_run(parser.parse_args()))
    except (FileNotFoundError, FileExistsError, ValueError, json.JSONDecodeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
