# ROI — referência para coleta de operandos

O LLM não é a autoridade do cálculo. Colete e valide os operandos no
`RoiInputs` e execute:

```bash
ai-audit calculate-roi \
  --hours-per-execution 2 \
  --executions-per-month 10 \
  --hourly-cost 100 \
  --error-rate 0.10 \
  --cost-per-error 50 \
  --output /path/to/roi.json
```

Valores ausentes, negativos ou fora da unidade esperada devem gerar pergunta
pendente ou erro. Nunca complete os operandos com uma suposição silenciosa.
