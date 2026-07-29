# Relatório completo — referência legada

O núcleo gera o relatório combinado com:

```bash
ai-audit render --workspace /path/to/workspace --draft
```

Use o agente para interpretar as evidências e produzir candidatos, não para
substituir `AuditResult`. Toda afirmação material deve manter `evidence_refs`;
perguntas pendentes, contradições e assumptions devem permanecer explícitas.
Não invente benchmarks, dados financeiros, citações ou conclusões jurídicas.
