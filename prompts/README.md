# Prompts do AI Audit

Os prompts são auxiliares do agente, não contratos de domínio. O contrato
canônico está em `docs/agent_contract.md` e os artefatos devem passar pela
validação Python.

Eles são executados pelo Codex ou Claude durante a auditoria; não exigem uma
chave de API ou outro provedor LLM adicional.

Para uma auditoria real, use nesta ordem:

1. `opportunity_extraction.md` para criar `working/opportunity_candidates.json`;
2. `risk_screening.md` para revisar categorias e perguntas de risco;
3. `ai-audit analyze-opportunities` e `ai-audit analyze-risks` para gerar o
   `AuditResult`.

Prompts de descoberta continuam disponíveis para preparar entrevistas, mas a
resposta do cliente precisa ser salva como evidência no workspace. Nenhum
prompt autoriza completar dados ausentes.
