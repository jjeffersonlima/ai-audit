# Directive: Process Analysis

## Objetivo

Interpretar as evidências com o agente e gerar candidatos normalizados de oportunidades comerciais e de automação.

## Preparação pelo agente

Ler:

- `working/evidence_index.json`;
- `working/audit_case.json`;
- `docs/opportunity_candidates.md`;
- `prompts/opportunity_extraction.md`.

O agente deve mapear processo, responsável, ferramenta, volume, frequência, tempo, gargalo, impacto e evidências. Não deve inventar ROI.

## Output do agente

Salvar uma lista em:

```text
working/opportunity_candidates.json
```

Cada candidato precisa de `evidence_refs`. Ausência de fonte deve gerar pergunta pendente, não oportunidade validada.

## Validação e execução

```bash
ai-audit analyze-opportunities --workspace /caminho/workspace
ai-audit validate-result --workspace /caminho/workspace
```

O núcleo calcula IDs, vincula riscos e cria o `AuditResult`.
