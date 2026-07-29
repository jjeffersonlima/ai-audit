# AI Audit

O AI Audit transforma documentos e informações de uma empresa em um
diagnóstico de oportunidades de automação/IA e riscos, sempre mostrando quais
evidências sustentam cada conclusão.

## O jeito mais fácil de usar

O uso recomendado é conversacional: abra este projeto no Codex ou Claude,
explique qual empresa será analisada e deixe o agente conduzir o processo.

Você não precisa decorar os comandos nem conhecer a estrutura interna. O agente
deve:

1. preparar ou confirmar a pasta local da auditoria;
2. orientar onde colocar os documentos da empresa;
3. analisar os arquivos recebidos;
4. fazer perguntas quando faltar informação;
5. executar as validações e cálculos;
6. apresentar um diagnóstico para revisão;
7. gerar os relatórios depois da sua aprovação.

No Codex ou Claude, use uma mensagem semelhante a esta:

```text
Quero realizar uma auditoria de oportunidades de automação/IA e riscos para
uma empresa.

Conduza o processo completo usando este projeto. Se o projeto ainda não
estiver disponível nesta conversa, prepare-o primeiro. Crie uma pasta local
separada para esta empresa e me diga exatamente onde devo colocar os arquivos.

Depois que eu fornecer os documentos:

1. Leia as instruções do projeto e o contrato em docs/agent_contract.md.
2. Organize e valide os arquivos recebidos.
3. Analise processos, gargalos, oportunidades, ROI e riscos.
4. Não invente dados. Quando algo faltar, faça uma pergunta objetiva.
5. Execute todas as validações antes de apresentar conclusões.
6. Mostre primeiro um diagnóstico para minha revisão.
7. Só gere a versão final dos relatórios depois que eu confirmar a revisão.

Ao longo do trabalho, explique em linguagem simples o que está fazendo e
pare somente quando precisar de documentos, uma decisão ou aprovação humana.
```

Essa é a forma principal de uso. Os comandos manuais abaixo existem para quem
quiser acompanhar ou automatizar partes do processo.

## O que o projeto entrega

- identificação das evidências usadas na análise;
- mapeamento de processos e gargalos;
- oportunidades de automação ou uso de IA;
- ROI calculado somente quando os dados necessários forem fornecidos;
- avaliação inicial de privacidade, segurança, viés, transparência e governança;
- perguntas pendentes quando faltarem informações;
- relatório executivo, relatório de oportunidades, relatório de riscos e matriz CSV;
- apresentação PPTX gerada a partir do resultado revisado.

O projeto não exige API key nem outra IA além da IA do Codex ou Claude. Ele não
coleta informações automaticamente, não inventa respostas e não substitui
revisão humana, parecer jurídico ou decisão de compliance.

## O que é necessário

- Python 3.10 ou superior;
- Codex, Claude Code ou outro agente capaz de ler arquivos e executar comandos;
- documentos da empresa autorizados para análise;
- uma pasta local separada para cada empresa.

## Instalação

Se você recebeu o projeto em uma pasta, abra essa pasta no Codex ou Claude.
Se ainda não o tiver, obtenha o repositório pelo próprio agente ou use:

```bash
git clone https://github.com/jjeffersonlima/ai-audit.git
cd ai-audit
```

Depois instale as dependências:

```bash
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

A instalação inclui o `python-pptx`, usado para gerar a apresentação.

## Se quiser acompanhar o processo manualmente

### 1. Crie a pasta da auditoria

Use uma pasta fora do repositório ou a pasta ignorada `.audit-workspaces/`.
Nunca coloque documentos reais diretamente no Git.

```bash
ai-audit init \
  --client "Empresa Exemplo" \
  --folder .audit-workspaces/empresa-exemplo
```

O comando cria as pastas onde ficarão os arquivos recebidos, os dados de
trabalho e os resultados.

### 2. Coloque os arquivos da empresa

Coloque os documentos na pasta `input/` criada pelo comando anterior. A
organização recomendada é:

```text
empresa-exemplo/
└── input/
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

São aceitos arquivos Markdown (`.md`), texto (`.txt`), JSON (`.json`) e CSV
(`.csv`). Para começar, forneça pelo menos um perfil da empresa, um
questionário ou contexto equivalente e uma descrição de processo, conversa ou
fluxo operacional.

Quanto mais concretas forem as informações sobre responsáveis, etapas,
ferramentas, frequência, volume, tempo, erros, retrabalho, custos e impacto,
mais útil será o diagnóstico.

### 3. Leia e valide os arquivos

```bash
ai-audit ingest \
  --folder .audit-workspaces/empresa-exemplo

ai-audit validate-case \
  --folder .audit-workspaces/empresa-exemplo
```

Se aparecer um erro, corrija o arquivo indicado antes de continuar. Ausência
de informação normalmente vira uma pergunta para a empresa, não um número
inventado.

### 4. Deixe o agente fazer a análise

Se você estiver executando os comandos manualmente, peça ao Codex ou Claude:

```text
Leia o conteúdo da pasta .audit-workspaces/empresa-exemplo e os documentos
docs/agent_contract.md e docs/opportunity_candidates.md.

Analise as evidências e salve os candidatos de oportunidade em
.audit-workspaces/empresa-exemplo/working/opportunity_candidates.json.

Use somente informações presentes nos arquivos. Use apenas referências de
evidência existentes. Não invente custos, volumes, prazos, benchmarks, pessoas
ou ROI. Separe fatos, hipóteses e recomendações. Registre lacunas e
contradições. Sinalize dados pessoais, financeiros, de saúde, biométricos,
emprego, crédito ou de crianças para revisão de risco.
```

O arquivo `working/opportunity_candidates.json` é necessário para a próxima
etapa. O agente deve criá-lo; o núcleo Python valida o conteúdo e transforma os
candidatos em um resultado estruturado.

### 5. Gere e valide o diagnóstico

```bash
ai-audit analyze-opportunities \
  --folder .audit-workspaces/empresa-exemplo

ai-audit analyze-risks \
  --folder .audit-workspaces/empresa-exemplo

ai-audit validate-result \
  --folder .audit-workspaces/empresa-exemplo

ai-audit quality \
  --folder .audit-workspaces/empresa-exemplo
```

O resultado canônico fica em:

```text
.audit-workspaces/empresa-exemplo/working/audit_result.json
```

Esse arquivo é a fonte única da verdade. Relatórios, matriz e apresentação
devem sair dele, sem uma nova interpretação do agente.

### 6. Revise e aprove

Antes de aprovar, confirme se as conclusões têm evidências suficientes, se os
números fazem sentido, se as perguntas foram respondidas e se os controles de
risco são adequados.

```bash
ai-audit approve \
  --folder .audit-workspaces/empresa-exemplo \
  --reviewer "Nome do Revisor"
```

Se a empresa aceitar pendências formalmente:

```bash
ai-audit approve \
  --folder .audit-workspaces/empresa-exemplo \
  --reviewer "Nome do Revisor" \
  --status approved_with_conditions
```

### 7. Gere os resultados finais

Para uma versão de revisão:

```bash
ai-audit render \
  --folder .audit-workspaces/empresa-exemplo \
  --draft
```

Para a versão final, o resultado precisa estar aprovado:

```bash
ai-audit render \
  --folder .audit-workspaces/empresa-exemplo
```

Os relatórios aparecem na pasta `output/`:

```text
Final Audit Report.md
Opportunity Audit Report.md
Risk Assessment Report.md
VALUE Scoring Matrix.csv
```

Para gerar a apresentação PPTX:

```bash
python execution/presentation_maker.py \
  --audit-result ".audit-workspaces/empresa-exemplo/working/audit_result.json" \
  --output ".audit-workspaces/empresa-exemplo/output/AI Audit - Empresa Exemplo.pptx"
```

A apresentação deve passar por revisão visual antes de ser entregue.

## Como melhorar a precisão

Forneça evidências concretas sobre:

- responsáveis e etapas do processo;
- ferramentas utilizadas e integrações;
- frequência, volume e tempo gasto;
- erros, retrabalho e exceções;
- impacto operacional e financeiro;
- dependências, restrições e orçamento;
- requisitos de privacidade, segurança e governança;
- objetivo estratégico da empresa.

Informações vagas podem gerar apenas hipóteses. O sistema deve declarar a
incerteza em vez de transformá-la em um número aparentemente preciso.

## Privacidade e segurança

- Use somente dados autorizados pela empresa.
- Mantenha os arquivos reais fora do Git ou dentro de `.audit-workspaces/`.
- Não coloque dados reais em testes, prompts ou exemplos versionados.
- Limite dados pessoais antes de compartilhá-los com qualquer agente.
- Defina responsáveis, retenção e descarte dos documentos do caso.
- Faça revisão humana antes de decisões comerciais, jurídicas ou regulatórias.

## Problemas comuns

**O agente não encontrou a pasta ou os arquivos**

Informe a pasta local correta e confirme se os arquivos foram colocados em
`input/`.

**O diagnóstico não começou**

Peça ao agente para executar `ingest`, `validate-case` e conferir se
`working/opportunity_candidates.json` foi criado.

**Apareceu uma pergunta pendente**

Responda ao agente com a informação da empresa ou aceite registrar a lacuna
como condição da recomendação. Não peça para ele inventar a resposta.

**A apresentação não foi gerada**

Confirme que a instalação foi concluída com `pip install -e .` e execute o
comando de PPTX mostrado acima.

## Documentação para o agente

- [Contrato para Codex, Claude e outros agentes](docs/agent_contract.md)
- [Formato dos candidatos de oportunidade](docs/opportunity_candidates.md)
