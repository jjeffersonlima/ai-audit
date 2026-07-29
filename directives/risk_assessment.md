# Directive: Risk Assessment

## Objetivo

Avaliar riscos das oportunidades que envolvem IA, dados pessoais ou decisões automatizadas.

## Critérios

- Privacidade e minimização de dados.
- Segurança e controle de acesso.
- Viés e discriminação.
- Transparência e revisão humana.
- Governança, retenção e responsabilidade.
- Jurisdição declarada no `audit_manifest.json`.

## Execução

A análise de risco é criada pelo módulo `risk_assessment` durante:

```bash
ai-audit analyze-opportunities --workspace /caminho/workspace
```

Também pode ser reexecutada de forma independente depois que o resultado de
oportunidades existir:

```bash
ai-audit analyze-risks --workspace /caminho/workspace
```

## Output

O resultado fica em `working/audit_result.json`, dentro de `risk_assessments`.

## Gates

- `not_applicable`: não envolve IA nem dados relevantes.
- `approved`: risco residual conhecido e aprovado.
- `approved_with_conditions`: pode avançar somente com as mitigações registradas.
- `blocked`: não pode ser priorizado para execução.
- `needs_information`: faltam evidências ou dados.

O resultado não é parecer jurídico. Itens de alto impacto devem ser encaminhados para revisão jurídica, de privacidade ou de segurança.
