# Scripts de execução legados

Os scripts desta pasta pertencem ao primeiro protótipo do projeto. Eles continuam no repositório para facilitar a migração, mas não são a fonte da verdade e não devem ser usados para iniciar novos casos.

Use o núcleo atual:

```bash
pip install -e .
ai-audit init --client "Empresa" --workspace /caminho/do/workspace
ai-audit ingest --workspace /caminho/do/workspace
ai-audit validate-case --workspace /caminho/do/workspace
ai-audit analyze-opportunities --workspace /caminho/do/workspace
ai-audit analyze-risks --workspace /caminho/do/workspace
ai-audit validate-result --workspace /caminho/do/workspace
ai-audit approve --workspace /caminho/do/workspace --reviewer "Revisor"
ai-audit render --workspace /caminho/do/workspace
```

O gerador de apresentações aceita o `AuditResult` diretamente:

```bash
PYTHONPATH=src python execution/presentation_maker.py \
  --audit-result /caminho/do/workspace/working/audit_result.json \
  --output "/caminho/do/workspace/output/AI Audit — Empresa — Apresentação.pptx"
```

`python-pptx` é instalado automaticamente por `pip install -e .` ou por
`requirements.txt`.
Use `--draft` somente durante a revisão de um resultado incompleto; a
apresentação final exige um `AuditResult` válido e aprovado.

O renderizador do CLI também cria relatórios separados de oportunidades e
riscos no mesmo diretório `output/`.
