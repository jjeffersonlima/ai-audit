# AI Audit

Framework para conduzir auditorias de IA em empresas, com foco em processos comerciais. Gera relatórios detalhados e apresentações executivas de forma semi-automatizada usando LLMs.

## Arquitetura

O sistema usa uma arquitetura de 3 camadas que separa responsabilidades:

| Camada | Função | Onde vive |
|--------|--------|-----------|
| **Directive** | SOPs em Markdown — o que fazer | `directives/` |
| **Orchestration** | O LLM — decisões e roteamento | Você (Claude, Gemini, etc.) |
| **Execution** | Scripts Python determinísticos | `execution/` |

Essa separação evita que erros do LLM se acumulem: lógica determinística fica em scripts, enquanto o LLM foca em interpretar dados e tomar decisões.

## Pré-requisitos

- Python 3.7+
- Acesso a um LLM (Claude, Gemini, ou similar)
- IDE com suporte a agentes (Cursor, Claude Code, Windsurf, etc.)

## Instalação

```bash
git clone https://github.com/SEU_USUARIO/ai-audit.git
cd ai-audit
pip install -r requirements.txt
```

## Workflow

O audit segue 5 etapas sequenciais:

1. **Client Onboarding** — Cria estrutura de pastas para o novo cliente
2. **Data Collection** — Coleta perfil, questionário, transcrições de calls
3. **Process Analysis** — Identifica gargalos, quick wins e ROI
4. **Report Generation** — Gera dossiê completo em pt-BR (~1000+ linhas)
5. **Presentation Generation** — Transforma o relatório em PPTX executivo (15 slides)

Para iniciar, abra o projeto no seu editor com agente e peça para executar o workflow de audit (`directives/ai_audit_workflow.md`).

## Estrutura do Projeto

```
ai-audit/
├── directives/          # SOPs - instruções de cada etapa
├── execution/           # Scripts Python determinísticos
├── prompts/             # Templates de prompts para o LLM
├── CLAUDE.md            # Instruções do agente (Claude)
├── AGENTS.md            # Instruções do agente (Cursor/generic)
├── GEMINI.md            # Instruções do agente (Gemini)
├── requirements.txt     # Dependências Python
└── .env.example         # Template de variáveis de ambiente
```

### Estrutura de pastas por cliente (gerada automaticamente)

```
[Cliente] - AI Audit/
├── .tmp/                          # Dados intermediários
├── Meeting Transcripts/           # Transcrições de calls
│   ├── Sales Calls/
│   ├── Discovery Calls/
│   └── Process Mapping Calls/
├── Client Context/                # Perfil e contexto do cliente
├── Process Documentation/         # Documentos, notas, formulários
│   ├── Onboarding Responses/
│   └── Process Notes ([Cargo])/   # Criados sob demanda
└── AI Audit/                      # Outputs finais
    ├── Final Audit Report.md
    ├── VALUE Scoring Matrix.csv
    └── AI Audit — [Cliente] — Apresentação.pptx
```

## Compatibilidade

As instruções do agente (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) são idênticas e carregam automaticamente em diferentes ambientes de IA. O framework funciona com qualquer LLM que suporte leitura de arquivos e execução de scripts.

## Relatório

O relatório final segue uma estrutura de 5 seções:

1. **Resumo Executivo** (2-3 páginas)
2. **Contexto e Estado Atual** (3-4 páginas)
3. **Análise Diagnóstica** (6-8 páginas)
4. **Avaliação de Oportunidades** (7-9 páginas) — backlog de 15-25 itens
5. **Recomendações e Roadmap** (4-5 páginas)

Todos os outputs são em português (pt-BR) com valores em R$.
