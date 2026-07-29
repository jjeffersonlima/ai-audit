# Apresentação: fonte canônica

Este prompt legado não deve mais extrair dados do relatório Markdown. O
relatório e a apresentação são renderizações independentes do mesmo
`working/audit_result.json`.

Use o adaptador determinístico:

```bash
PYTHONPATH=src python execution/presentation_maker.py \
  --audit-result /path/to/workspace/working/audit_result.json \
  --output "/path/to/workspace/output/AI Audit — Empresa — Apresentação.pptx"
```

O agente não deve preencher benchmarks, quotes, ROI ou métricas ausentes. Em
modo `--draft`, o adaptador mostra `Dados pendentes` ou `—`; na versão final,
campos incompletos fazem a validação falhar.
