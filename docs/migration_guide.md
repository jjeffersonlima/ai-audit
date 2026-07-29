# Migração do protótipo para o pipeline canônico

O protótipo anterior usava arquivos temporários e scripts independentes. O
fluxo atual usa um workspace por auditoria e `working/audit_result.json` como
fonte única da verdade.

| Antes | Atual |
|---|---|
| `execution/data_collector.py --client-dir ...` | `ai-audit init` + `ai-audit ingest` |
| `.tmp/client_data.json` | `working/audit_case.json` |
| `execution/analyzer.py` com score fixo | agente gera candidatos + `analyze-opportunities` |
| risco embutido no relatório | `analyze-risks` e `risk_assessments` |
| relatório alimenta PPTX por reextração | Markdown, CSV e PPTX derivam do `AuditResult` |

Os scripts em `execution/` continuam disponíveis durante um ciclo de
compatibilidade, mas estão marcados como legados. Novos casos devem usar o CLI.

## Passos

1. Crie um workspace com `ai-audit init`.
2. Copie os arquivos autorizados para `input/`.
3. Execute `ingest` e `validate-case`.
4. Faça o agente gerar `working/opportunity_candidates.json` conforme
   `docs/opportunity_candidates.md` e `prompts/opportunity_extraction.md`.
5. Execute `analyze-opportunities`, `analyze-risks` e `validate-result`.
6. Faça a aprovação humana e só então gere os outputs finais.

Não copie dados reais para o repositório e não use o score do script legado como
evidência: ele foi removido por não ser suportado por dados.
