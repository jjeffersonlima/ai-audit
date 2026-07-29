# Candidatos de oportunidade

O agente deve salvar uma lista JSON em `working/opportunity_candidates.json` depois de ler e interpretar as evidências. O arquivo é uma proposta normalizada; o núcleo Python valida IDs e não aceita evidências inexistentes.

Exemplo:

```json
[
  {
    "title": "Follow-up automático",
    "problem": "O time registra o follow-up manualmente após reuniões.",
    "proposed_solution": "Criar uma tarefa no CRM após o registro da reunião.",
    "evidence_refs": ["E-abc123"],
    "process_refs": ["process-follow-up"],
    "dependencies": ["CRM com API disponível"],
    "implementation_effort": "low",
    "timeline": "2 semanas",
    "involves_ai": false,
    "data_categories": ["contact"],
    "confidence_level": "medium",
    "confidence_rationale": "Relatado em transcrição e confirmado no questionário.",
    "business_impact": {
      "hours_per_week": 8
    },
    "priority_dimensions": {
      "value": "medium",
      "feasibility": "high"
    },
    "process": {
      "process_id": "process-follow-up",
      "name": "Follow-up",
      "steps": [
        {"name": "Registrar atividade", "owner": "Vendas", "tools": ["CRM"]}
      ]
    },
    "roi_inputs": {
      "base": {
        "hours_per_execution": 2,
        "executions_per_month": 10,
        "hourly_cost": 100,
        "error_rate": 0.1,
        "cost_per_error": 50
      }
    }
  }
]
```

Regras:

- `evidence_refs` é obrigatório e deve apontar para IDs presentes no snapshot ingerido.
- `confidence_level` não é probabilidade estatística.
- Números de ROI não devem ser inventados neste arquivo; devem ser calculados pelo módulo determinístico.
- `roi_inputs` é opcional, mas quando presente deve conter operandos fornecidos ou confirmados; o núcleo calcula `roi_scenarios`.
- `process` é opcional; quando presente, cada etapa deve manter responsável, ferramentas e evidências conhecidas.
- Ausência de informação deve ser registrada em `assumptions` ou `pending_questions`.
- Se `involves_ai` for verdadeiro ou houver dados sensíveis, o candidato deve passar pelo módulo de riscos.
