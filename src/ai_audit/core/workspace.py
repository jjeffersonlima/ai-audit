"""Workspace lifecycle helpers."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .models import AuditManifest, write_json


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "cliente"


def init_workspace(client_name: str, workspace: str | Path, *, force: bool = False) -> Path:
    root = Path(workspace).resolve()
    if root.exists() and any(root.iterdir()) and not force:
        raise FileExistsError(f"Workspace não está vazio: {root}. Use --force somente se necessário.")
    root.mkdir(parents=True, exist_ok=True)
    for relative in (
        "input/Client Context",
        "input/Meeting Transcripts/Sales Calls",
        "input/Meeting Transcripts/Discovery Calls",
        "input/Meeting Transcripts/Process Mapping Calls",
        "input/Process Documentation/Onboarding Responses",
        "working",
        "output",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = AuditManifest(
        audit_id=f"AUD-{_slug(client_name)}",
        client_id=_slug(client_name),
        client_name=client_name,
        created_at=now,
        updated_at=now,
    )
    write_json(root / "working" / "audit_manifest.json", manifest)
    (root / "README.md").write_text(
        f"# Workspace de AI Audit — {client_name}\n\n"
        "Coloque os arquivos de entrada em `input/`. Artefatos intermediários ficam em `working/` e entregáveis em `output/`.\n",
        encoding="utf-8",
    )
    return root
