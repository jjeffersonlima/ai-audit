# AI Audit

O AI Audit transforma documentos e informações de uma empresa em um
diagnóstico de oportunidades de automação/IA e riscos, sempre com referências
às evidências utilizadas.

Ele funciona em conjunto com o Codex, Claude ou outro agente capaz de ler
arquivos e executar comandos. A IA interpreta os documentos; o projeto valida
os dados, calcula ROI, aplica gates de risco e gera os entregáveis.

## O que você recebe

- Índice das evidências usadas no diagnóstico.
- Mapeamento de processos e gargalos identificados.
- Oportunidades de automação ou uso de IA.
- Cálculo determinístico de ROI quando os dados necessários forem fornecidos.
- Avaliação inicial de riscos de privacidade, segurança, viés, transparência e governança.
- Perguntas pendentes quando faltarem informações.
- Relatório executivo, relatório de oportunidades, relatório de riscos e matriz CSV.
- Apresentação PPTX gerada a partir do mesmo resultado validado.

## O que é necessário

- Python 3.10 ou superior.
- Codex, Claude Code ou outro agente com acesso aos arquivos locais.
- Documentos da empresa com autorização para uso.
- Uma pasta de workspace separada para cada empresa.

O projeto não exige API key nem outra assinatura de LLM. No uso normal, a IA
é a própria IA disponível no Codex ou Claude.

O sistema não coleta dados automaticamente, não inventa informações e não
substitui revisão humana, parecer jurídico ou decisão de compliance.

## Instalação

```bash
git clone https://github.com/jjeffersonlima/ai-audit.git
cd ai-audit
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

A instalação inclui `python-pptx`, usado para gerar a apresentação.

Se não quiser instalar o pacote, execute os comandos usando
`PYTHONPATH=src python -m ai_audit` no lugar de `ai-audit`.

## Uso completo em uma empresa

### 1. Crie um workspace

Use uma pasta fora do repositório ou a pasta ignorada `.audit-workspaces/`.
Nunca coloque documentos reais diretamente no Git.

```bash
ai-audit init \
  --client "Empresa Exemplo" \
  --workspace .audit-workspaces/empresa-exemplo
```

O comando cria as pastas `input/`, `working/` e `output/`.

### 2. Adicione os documentos da empresa

Coloque os arquivos em `input/`. A organização abaixo é recomendada porque
ajuda o sistema a identificar o tipo de cada fonte:

```text
.audit-workspaces/empresa-exemplo/input/
├── Client Context/
│   └── Client_Profile.md
├── Meeting Transcripts/
│   ├── Discovery Calls/
│   ├── Process Mapping Calls/
│   └── Sales Calls/
└── Process Documentation/
    ├── Onboarding Responses/
    └── Process Notes/
```

Formatos atualmente aceitos:

- Markdown (`.md`)
- Texto (`.txt`)
- JSON (`.json`)
- CSV (`.csv`)

Para um diagnóstico inicial, forneça pelo menos:

- perfil ou contexto da empresa;
- questionário de onboarding ou informações equivalentes;
- descrição de pelo menos um processo, conversa ou fluxo operacional.

Quanto mais completos forem os dados sobre frequência, volume, tempo, erros,
retrabalho, ferramentas, custos e responsáveis, mais precisa será a análise.

### 3. Ingira e valide os dados

```bash
ai-audit ingest \
  --workspace .audit-workspaces/empresa-exemplo

ai-audit validate-case \
  --workspace .audit-workspaces/empresa-exemplo
```

Esses comandos criam em `working/`:

- `audit_manifest.json`: identificação, escopo e jurisdição do caso;
- `evidence_index.json`: fontes, hashes, tipo, idioma e sensibilidade;
- `audit_case.json`: dados normalizados e perguntas pendentes.

Se a validação retornar erro, corrija os arquivos de entrada antes de
continuar. Avisos de informação ausente não são falhas: eles se tornam
perguntas para a empresa.

### 4. Peça ao Codex ou Claude para analisar as evidências

Esta é a etapa em que a IA interpreta o conteúdo empresarial. Abra o projeto
no Codex ou Claude e envie um prompt como este, ajustando o caminho do
workspace:

```text
Você está trabalhando no projeto AI Audit.

Analise o workspace:
.audit-workspaces/empresa-exemplo

Leia primeiro:
- docs/agent_contract.md
- docs/opportunity_candidates.md
- working/evidence_index.json
- working/audit_case.json

Crie uma lista JSON de candidatos em:
working/opportunity_candidates.json

Regras obrigatórias:
1. Use somente informações presentes nas evidências.
2. Use apenas evidence_refs existentes no evidence_index.json.
3. Não invente custos, volumes, prazos, benchmarks, pessoas ou ROI.
4. Separe fato observado, hipótese e recomendação.
5. Registre lacunas e contradições em vez de preenchê-las com suposições.
6. Sinalize dados pessoais, financeiros, de saúde, biométricos, de emprego,
   crédito ou de crianças para revisão de risco.
7. Não calcule ROI manualmente; preencha roi_inputs somente quando os
   operandos estiverem explicitamente presentes nas evidências.
8. Salve somente JSON válido no arquivo indicado.

Antes de terminar, confirme que todos os evidence_refs existem.
```

O arquivo `working/opportunity_candidates.json` é obrigatório. Sem ele, o
comando de análise não pode gerar o diagnóstico.

### 5. Gere oportunidades e riscos

Execute os comandos na ordem:

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

O resultado principal será salvo em:

```text
.audit-workspaces/empresa-exemplo/working/audit_result.json
```

Esse arquivo é a fonte única da verdade. Relatórios, matriz e apresentação
devem ser gerados a partir dele, nunca de uma nova interpretação do agente.

O comando `quality` gera `working/quality_report.json`, com informações sobre
rastreabilidade, pendências, contradições e itens bloqueados. Ele ajuda na
revisão, mas não substitui o julgamento humano sobre a qualidade da
recomendação.

### 6. Faça a revisão humana

Antes de aprovar, verifique:

- se cada conclusão está apoiada por evidências suficientes;
- se os números e fórmulas fazem sentido;
- se as perguntas pendentes foram respondidas;
- se as contradições foram resolvidas;
- se os riscos e controles são adequados;
- se a recomendação é executável pela empresa.

Para aprovar um resultado completo:

```bash
ai-audit approve \
  --workspace .audit-workspaces/empresa-exemplo \
  --reviewer "Nome do Revisor"
```

Se ainda houver pendências que foram aceitas formalmente:

```bash
ai-audit approve \
  --workspace .audit-workspaces/empresa-exemplo \
  --reviewer "Nome do Revisor" \
  --status approved_with_conditions
```

Uma aprovação condicional deve ser tratada como resultado com ressalvas, não
como confirmação de que todas as informações foram validadas.

### 7. Gere os entregáveis

Para gerar uma versão de revisão:

```bash
ai-audit render \
  --workspace .audit-workspaces/empresa-exemplo \
  --draft
```

Para gerar a versão final, o `AuditResult` precisa estar aprovado:

```bash
ai-audit render \
  --workspace .audit-workspaces/empresa-exemplo
```

Os relatórios serão criados em `output/`:

```text
Final Audit Report.md
Opportunity Audit Report.md
Risk Assessment Report.md
VALUE Scoring Matrix.csv
```

Para gerar também a apresentação:

```bash
python execution/presentation_maker.py \
  --audit-result ".audit-workspaces/empresa-exemplo/working/audit_result.json" \
  --output ".audit-workspaces/empresa-exemplo/output/AI Audit - Empresa Exemplo.pptx"
```

Revise visualmente a apresentação antes de entregá-la, especialmente textos
longos, números, pendências e páginas com muitos itens.

## Como interpretar os arquivos

| Arquivo | Finalidade |
|---|---|
| `evidence_index.json` | Fontes efetivamente lidas pelo sistema |
| `audit_case.json` | Dados normalizados do caso |
| `opportunity_candidates.json` | Interpretação produzida pelo agente |
| `audit_result.json` | Diagnóstico canônico validado |
| `quality_report.json` | Indicadores de rastreabilidade e pendências |
| `Final Audit Report.md` | Síntese executiva do diagnóstico |
| `Opportunity Audit Report.md` | Oportunidades, impacto, ROI e execução |
| `Risk Assessment Report.md` | Riscos e controles necessários |
| `VALUE Scoring Matrix.csv` | Matriz para priorização e discussão comercial |

## Como obter um diagnóstico melhor

Inclua evidências concretas sobre:

- responsáveis e etapas do processo;
- ferramentas utilizadas e integrações;
- frequência, volume e tempo gasto;
- erros, retrabalho e exceções;
- impacto operacional e financeiro;
- dependências, restrições e orçamento;
- requisitos de privacidade, segurança e governança;
- objetivo estratégico da empresa.

Informações vagas podem gerar somente hipóteses. O sistema deve declarar a
incerteza em vez de transformá-la em um número aparentemente preciso.

## Privacidade e segurança

- Use somente dados autorizados pela empresa.
- Mantenha o workspace fora do Git ou dentro de `.audit-workspaces/`.
- Não coloque dados reais em testes, prompts ou exemplos versionados.
- Limite dados pessoais antes de compartilhá-los com qualquer agente.
- Defina responsáveis, retenção e descarte dos documentos do caso.
- Faça revisão humana antes de decisões comerciais, jurídicas ou regulatórias.

## Solução de problemas

**`Manifesto não encontrado`**

Execute `ai-audit init` antes de `ingest`.

**`AuditCase inválido`**

Corrija arquivos JSON/CSV inválidos, caminhos de entrada e informações
obrigatórias; depois execute novamente `ingest` e `validate-case`.

**`Candidatos não encontrados`**

Peça ao Codex ou Claude para criar
`working/opportunity_candidates.json` conforme o prompt deste README.

**`AuditResult inválido`**

Verifique referências de evidência, processos, riscos e perguntas pendentes
antes de tentar aprovar ou renderizar.

**A apresentação não foi gerada**

Confirme que o pacote foi instalado com `pip install -e .` e execute o comando
de apresentação mostrado neste README.

## Documentação operacional

- [Contrato para Codex, Claude e outros agentes](docs/agent_contract.md)
- [Formato dos candidatos de oportunidade](docs/opportunity_candidates.md)
