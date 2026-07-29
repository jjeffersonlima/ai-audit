# Análise de gargalos — referência legada

Use `prompts/opportunity_extraction.md` para gerar candidatos normalizados.

O agente deve identificar etapas, responsáveis, ferramentas, frequência,
volume, gargalo e impacto somente quando houver evidência. Não deve estimar
horas, custo, benchmark ou ROI sem operandos fornecidos pelo cliente. Salve o
resultado em `working/opportunity_candidates.json` e inclua `evidence_refs` em
cada candidato.
