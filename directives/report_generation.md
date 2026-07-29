# Directive: Report Generation

## Objetivo

Renderizar os resultados validados em relatório e matriz, sem reextrair dados de outro output.

## Pré-requisitos

- `working/audit_result.json` existente;
- validação concluída;
- aprovação humana ou modo explícito de rascunho.

## Execução

Rascunho:

```bash
ai-audit render --workspace /caminho/workspace --draft
```

Versão final:

```bash
ai-audit approve --workspace /caminho/workspace --reviewer "Nome"
ai-audit render --workspace /caminho/workspace
```

## Outputs

- `output/Final Audit Report.md`;
- `output/Opportunity Audit Report.md`;
- `output/Risk Assessment Report.md`;
- `output/VALUE Scoring Matrix.csv`.

## Regras

- O relatório deve refletir o `AuditResult`.
- Números devem ser reproduzíveis pelo núcleo.
- Findings e oportunidades sem evidência não podem ser apresentados como fatos.
- Perguntas pendentes, assumptions e riscos residuais devem aparecer no output.
