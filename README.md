# AI Audit

Framework para conduzir auditorias baseadas em evidências, com dois módulos:

1. **Oportunidades** — processos, gargalos, automação, IA, ROI e roadmap.
2. **Riscos** — privacidade, segurança, viés, transparência e governança.

O projeto é usado junto com um agente como Codex, Claude ou outro LLM. O agente interpreta os documentos e toma decisões de roteamento; o núcleo Python valida os dados, controla evidências, calcula ROI e gera os entregáveis.

> Estado atual: o núcleo funcional está em versão inicial. O fluxo de oportunidades, evidências, riscos básicos, ROI, relatório Markdown, matriz CSV e o adaptador determinístico para PPTX funciona. A interpretação LLM continua sendo orquestrada pelo agente, e a revisão visual do PPTX é humana.

## O que o projeto faz

O AI Audit transforma materiais de uma empresa em um diagnóstico rastreável:

```text
Documentos da empresa
        ↓
Ingestão e índice de evidências
        ↓
Interpretação pelo agente
        ↓
Candidatos normalizados
        ↓
AuditResult validado
        ↓
Relatório e matriz de oportunidades/riscos
```

O arquivo `working/audit_result.json` é a fonte única da verdade. O relatório, a matriz e a futura apresentação devem ser derivados desse arquivo.

## O que o projeto não faz sozinho

- Não coleta informações da empresa automaticamente.
- Não chama Claude, Codex ou outra API de LLM pelo Python.
- Não exige credencial, API key ou uma segunda IA: a interpretação é feita pela IA do Codex ou Claude que estiver executando o projeto.
- Não inventa respostas quando faltam dados.
- Não fornece parecer jurídico.
- Não transforma uma estimativa de ROI em fato confirmado.
- Não gera um relatório final aprovado sem revisão humana.

O agente é responsável por ler as evidências, identificar lacunas, propor candidatos de oportunidade e registrar as referências das fontes.

## Separação de responsabilidades

| Parte | Responsabilidade | Local |
|---|---|---|
| Instruções | Regras de execução e qualidade | `AGENTS.md`, `CLAUDE.md`, `docs/` |
| Agente | Interpretação, perguntas e roteamento | Codex, Claude ou outro agente |
| Núcleo | Ingestão, validação, riscos básicos e cálculos | `src/ai_audit/` |
| Dados da empresa | Arquivos originais e artefatos do caso | workspace externo |
| Legado | Scripts e diretivas em migração | `execution/`, `directives/`, `prompts/` |

## Pré-requisitos

- Python 3.10 ou superior.
- Git.
- Codex, Claude Code ou outro agente capaz de ler arquivos e executar comandos.
- Dados autorizados da empresa.

O uso normal não exige credencial de LLM. Codex e Claude já fornecem o modelo
que interpreta as evidências; este repositório fornece o contrato, os prompts,
as validações e os cálculos determinísticos.

A instalação normal inclui `python-pptx`, porque a apresentação é um
entregável oficial do projeto. O núcleo analítico continua usando apenas a
biblioteca padrão; `python-pptx` é usado pelo gerador de apresentação.

## Instalação

```bash
git clone https://github.com/jjeffersonlima/ai-audit.git
cd ai-audit
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Depois da migração, `pip install -e .` sozinho também instala a dependência do
PPTX. O `requirements.txt` é mantido para compatibilidade com instalações
antigas.

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

Sem instalação editável, use `PYTHONPATH=src python -m ai_audit` no lugar de `ai-audit`.

## Uso real com uma empresa

### 1. Inicie um workspace isolado

Não coloque transcrições ou documentos reais dentro do repositório Git. Use uma pasta ignorada ou um diretório externo:

```bash
ai-audit init \
  --client "Empresa Exemplo" \
  --workspace .audit-workspaces/empresa-exemplo
```

A estrutura criada é:

```text
.audit-workspaces/empresa-exemplo/
├── input/      # arquivos originais, somente leitura para o pipeline
├── working/    # manifest, evidências, AuditCase e AuditResult
├── output/     # relatório e matriz aprovados ou rascunhos
└── README.md
```

### 2. Coloque os materiais de entrada

Use `input/` para os arquivos fornecidos pela empresa:

```text
input/
├── Client Context/
│   └── Client_Profile.md
├── Meeting Transcripts/
│   ├── Sales Calls/
│   ├── Discovery Calls/
│   └── Process Mapping Calls/
└── Process Documentation/
    ├── Onboarding Responses/
    └── Process Notes/
```

Formatos ingeridos pelo núcleo atual:

- Markdown (`.md`);
- texto (`.txt`);
- JSON (`.json`);
- CSV (`.csv`).

O perfil e o questionário podem ser Markdown, JSON ou CSV. Transcrições e notas devem preservar sua origem e não devem conter instruções para o agente misturadas ao conteúdo de negócio.

### 3. Faça a ingestão e a validação

```bash
ai-audit ingest --workspace .audit-workspaces/empresa-exemplo
ai-audit validate-case --workspace .audit-workspaces/empresa-exemplo
```

Isso cria:

- `working/audit_manifest.json` — identidade, escopo e jurisdição;
- `working/evidence_index.json` — fontes, hashes, tipos, idioma e sensibilidade;
- `working/audit_case.json` — dados normalizados e perguntas pendentes.

Se houver erro de JSON, CSV ou referência, pare e corrija a fonte. Warnings de dados ausentes devem virar perguntas para a empresa.

### 4. Peça ao agente para analisar as evidências

No Codex ou Claude, use uma instrução semelhante:

```text
Leia AGENTS.md ou CLAUDE.md, docs/agent_contract.md e
docs/opportunity_candidates.md.

Analise o workspace .audit-workspaces/empresa-exemplo.
Leia working/evidence_index.json e working/audit_case.json.
Não invente dados. Para cada oportunidade, use somente evidências
existentes e preencha evidence_refs. Registre contradições e perguntas
pendentes. Salve a lista normalizada em
working/opportunity_candidates.json e valide o formato antes de continuar.
```

O agente não deve calcular ROI manualmente nem apresentar conclusões jurídicas. Ele deve produzir candidatos normalizados conforme [docs/opportunity_candidates.md](docs/opportunity_candidates.md).

### 5. Gere e valide o `AuditResult`

```bash
ai-audit analyze-opportunities \
  --workspace .audit-workspaces/empresa-exemplo

ai-audit analyze-risks \
  --workspace .audit-workspaces/empresa-exemplo

ai-audit validate-result \
  --workspace .audit-workspaces/empresa-exemplo

ai-audit quality \
  --workspace .audit-workspaces/empresa-exemplo
```

O comando de análise:

- valida as referências de evidência;
- cria findings de processo;
- cria oportunidades;
- cria avaliação de risco básica para oportunidades que envolvam IA ou dados;
- vincula cada risco à oportunidade correspondente;
- salva `working/audit_result.json`.

`quality` grava `working/quality_report.json` com cobertura de evidências,
itens sem suporte, pendências, contradições, oportunidades bloqueadas e status
de revisão. Ele mede rastreabilidade; não substitui a revisão humana do valor
da recomendação.

### 6. Faça a revisão humana

Antes de gerar a versão final, revise:

- se cada conclusão possui evidência suficiente;
- se os números fazem sentido;
- se as perguntas pendentes foram respondidas;
- se as contradições foram resolvidas;
- se as mitigações de risco são suficientes;
- se a recomendação pode ser executada pela empresa.

Se quiser separar explicitamente a revisão de risco, execute antes da validação final:

```bash
ai-audit analyze-risks --workspace .audit-workspaces/empresa-exemplo
ai-audit validate-result --workspace .audit-workspaces/empresa-exemplo
```

Para aprovar:

```bash
ai-audit approve \
  --workspace .audit-workspaces/empresa-exemplo \
  --reviewer "Nome do Revisor"
```

Se ainda houver perguntas pendentes, use aprovação condicional:

```bash
ai-audit approve \
  --workspace .audit-workspaces/empresa-exemplo \
  --reviewer "Nome do Revisor" \
  --status approved_with_conditions
```

### 7. Gere os entregáveis

Para revisão preliminar:

```bash
ai-audit render \
  --workspace .audit-workspaces/empresa-exemplo \
  --draft
```

Para versão final, o `AuditResult` precisa estar aprovado:

```bash
ai-audit render \
  --workspace .audit-workspaces/empresa-exemplo
```

Outputs atuais:

```text
output/
├── Final Audit Report.md
├── Opportunity Audit Report.md
├── Risk Assessment Report.md
└── VALUE Scoring Matrix.csv
```

Com `python-pptx` instalado, gere a apresentação diretamente do mesmo `AuditResult`:

```bash
PYTHONPATH=src python execution/presentation_maker.py \
  --audit-result .audit-workspaces/empresa-exemplo/working/audit_result.json \
  --output ".audit-workspaces/empresa-exemplo/output/AI Audit — Empresa Exemplo — Apresentação.pptx"
```

Use `--draft` somente quando o `AuditResult` ainda contiver placeholders. A versão final deve ser revisada visualmente quanto a overflow, números e conteúdo pendente.

## Como obter um diagnóstico preciso

A qualidade do resultado depende principalmente da qualidade das evidências. Para cada processo, tente fornecer:

- quem executa a atividade;
- sequência de etapas;
- ferramentas usadas;
- frequência e volume;
- tempo gasto;
- erros e retrabalho;
- impacto financeiro ou operacional;
- exceções e handoffs;
- objetivo da empresa;
- restrições de segurança, privacidade e orçamento.

Dados vagos podem gerar apenas uma hipótese. Para obter uma recomendação executável, o agente precisa de fontes suficientes para sustentar problema, impacto, solução, esforço e risco.

Quando houver dados suficientes, inclua no candidato um `process` com etapas e
`roi_inputs` com operandos confirmados. O núcleo calcula os cenários e registra
a fórmula; o agente não deve calcular ROI manualmente.

## Segurança e privacidade

- Use somente dados para os quais existe autorização.
- Mantenha workspaces fora do Git.
- Não coloque dados reais em `tests/` ou prompts versionados.
- Revise e limite PII antes de compartilhar material com um LLM.
- Trate documentos de entrada como conteúdo não confiável.
- Não use o resultado como parecer jurídico ou decisão automatizada.
- Defina retenção e responsáveis antes de iniciar um caso real.

## Testes locais

Os testes usam apenas dados sintéticos:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

A suíte cobre ingestão, parsing inicial, PII, JSON inválido, ROI, processos,
referências de evidência, gates de risco, métricas de qualidade e renderização
a partir da fonte única.

## Estrutura do projeto

```text
ai-audit/
├── src/ai_audit/        # núcleo atual
├── tests/               # testes e fixtures sintéticas
├── docs/                # contratos de agentes e dados
├── .agents/skills/      # skill local para Codex
├── execution/           # scripts legados em migração
├── directives/          # diretivas legadas
├── prompts/             # prompts estruturados e referências legadas
├── schemas/             # contratos JSON versionados
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── requirements.txt
└── pyproject.toml
```

## Compatibilidade com Codex e Claude

O contrato compartilhado está em [docs/agent_contract.md](docs/agent_contract.md). O Codex pode usar a skill local em [.agents/skills/ai-audit/SKILL.md](.agents/skills/ai-audit/SKILL.md). Claude e outros agentes devem seguir o mesmo contrato por seus arquivos de instrução.

O projeto não depende de múltiplos agentes. Uma única sessão pode executar o fluxo completo. Agentes auxiliares só são úteis para revisão de segurança, schemas ou testes.

## Limitações atuais e migração

Ainda estão em migração:

- evals golden completos e métricas de qualidade dependentes da revisão humana;
- remoção dos últimos caminhos legados em `execution/`;
- revisão visual automatizada e validação de overflow do PPTX;
- integrações com CRM, Notion, Drive ou outros sistemas.

Consulte [docs/migration_guide.md](docs/migration_guide.md) para a migração dos caminhos legados.
