# Prompt: Presentation Data Extraction

**When to use:** After the Final Audit Report is completed and approved, to extract structured data for PPTX generation.

**Input:** The complete Final Audit Report (Markdown).

**Output:** A single JSON object with all data needed for the 15-slide executive presentation.

---

**Prompt Template:**

You are a data extraction specialist. Your task is to read the complete AI Audit Report below and extract ONLY the most impactful data points into a structured JSON format for an executive presentation.

## RULES

1. **Be concise.** Slide text must be SHORT. Max 15 words per bullet. Max 8 words per card title.
2. **Prioritize numbers.** Always prefer quantified data (%, R$, hours, ratios) over qualitative statements.
3. **Use the report's language.** Keep all text in Portuguese (pt-BR) as written in the report.
4. **CRITICAL: Proper Portuguese accents.** All text MUST use correct pt-BR diacritics (ç, ã, õ, é, ê, á, à, ú, í, ó). Examples: "Prospecção" (not "Prospeccao"), "Automação" (not "Automacao"), "Geração" (not "Geracao"), "Nutrição" (not "Nutricao"), "Reunião" (not "Reuniao"), "Transformação" (not "Transformacao"), "após" (not "apos"), "períodos" (not "periodos"). Never omit accents.
5. **Extract direct quotes.** Include at least 1 verbatim quote from transcripts with attribution.
6. **Limit discoveries to exactly 3.** Pick the 3 most critical/impactful findings.
7. **Limit priorities to exactly 5.** Pick the top 5 from the roadmap.
8. **Benchmarks:** If the report has competitive benchmarks, extract 5 metrics. If not, synthesize from the diagnostic data.

## OUTPUT JSON SCHEMA

Return ONLY valid JSON (no markdown fences, no commentary). Follow this exact schema:

```json
{
  "client_name": "string — Company name",

  "agenda": {
    "block_1": {"time": "0–5 min", "title": "string", "description": "string"},
    "block_2": {"time": "5–12 min", "title": "string", "description": "string"},
    "block_3": {"time": "12–22 min", "title": "string", "description": "string"},
    "block_4": {"time": "22–30 min", "title": "string", "description": "string"}
  },

  "diagnostico_kpis": [
    {
      "value": "string — e.g. '23%'",
      "label": "string — e.g. 'Win Rate Atual'",
      "description": "string — 1 sentence context",
      "color": "green|red|amber — semantic color based on positive/negative/neutral"
    }
  ],

  "descobertas_criticas": [
    {
      "number": "01",
      "title": "string — max 5 words",
      "subtitle": "string — max 10 words",
      "bullets": ["string", "string", "string"],
      "color": "red|amber|blue"
    }
  ],

  "descoberta_1_detail": {
    "section_label": "DESCOBERTA 01",
    "title": "string — descriptive title",
    "metrics": [
      {"value": "string", "label": "string", "sublabel": "string"}
    ],
    "quote": {
      "text": "string — verbatim quote from transcript",
      "attribution": "string — Name, Role"
    },
    "callout": "string — key insight or implication (1-2 sentences)"
  },

  "descoberta_2_detail": {
    "section_label": "DESCOBERTA 02",
    "title": "string",
    "flow_steps": [
      {"step": "1", "label": "string — max 3 words"},
      {"step": "2", "label": "string"},
      {"step": "3", "label": "string"},
      {"step": "4", "label": "string"}
    ],
    "storage_locations": ["string", "string", "string"],
    "bottom_stats": [
      {"value": "string", "label": "string"}
    ]
  },

  "descoberta_3_detail": {
    "section_label": "DESCOBERTA 03",
    "title": "string",
    "funnel_stages": [
      {"label": "string", "value": "string", "width_pct": 100},
      {"label": "string", "value": "string", "width_pct": 75},
      {"label": "string", "value": "string", "width_pct": 50},
      {"label": "string", "value": "string", "width_pct": 25}
    ],
    "info_panel": {
      "title": "string",
      "bullets": ["string", "string", "string"]
    }
  },

  "custo_status_quo": [
    {
      "value": "string — big number e.g. '193h'",
      "label": "string — what it represents",
      "sublabel": "string — additional context"
    }
  ],

  "benchmarks": {
    "metrics": ["string — metric name x5"],
    "client_values": ["string x5"],
    "market_avg": ["string x5"],
    "top_25": ["string x5"],
    "gap": ["string — e.g. '-52%' x5"]
  },

  "prioridades": [
    {
      "number": "P1",
      "name": "string — max 6 words",
      "roi": "string — e.g. '5:1'",
      "payback": "string — e.g. '2 meses'",
      "timeline": "string — e.g. 'Mês 1-2'",
      "phase": "string — e.g. 'Quick Win'",
      "color": "green|blue|amber"
    }
  ],

  "quick_wins_detail": [
    {
      "priority": "P1",
      "title": "string",
      "problem": "string — 1 sentence",
      "solution": "string — 1 sentence",
      "tools": "string — tool names",
      "investment": "string — R$ range",
      "expected_result": "string — 1 sentence",
      "timeline": "string"
    }
  ],

  "transformation_detail": [
    {
      "priority": "P3",
      "title": "string",
      "problem": "string",
      "solution": "string",
      "tools": "string",
      "investment": "string",
      "expected_result": "string",
      "timeline": "string"
    }
  ],

  "roi_consolidado": {
    "investment": {"value": "string — e.g. 'R$ 80-130k'", "label": "Investimento Total"},
    "return": {"value": "string", "label": "Retorno Estimado"},
    "roi": {"value": "string — e.g. '5:1 a 9:1'", "label": "ROI"},
    "payback": {"value": "string — e.g. '2-3 meses'", "label": "Payback Médio"}
  },

  "resultados_esperados": [
    {
      "metric": "string — metric name",
      "before": "string — current value",
      "after": "string — expected value",
      "variation": "string — e.g. '+150%'"
    }
  ],

  "proximos_passos": [
    {
      "number": "1",
      "title": "string — action title",
      "description": "string — 1-2 sentences",
      "timeline": "string — e.g. 'Semana 1'"
    }
  ]
}
```

## IMPORTANT NOTES

- `diagnostico_kpis`: Extract exactly 3 KPIs that best summarize the current state
- `descobertas_criticas`: Exactly 3 critical discoveries
- `custo_status_quo`: Exactly 3 big-impact numbers (hours wasted, money lost, revenue at risk)
- `benchmarks.metrics`: Exactly 5 benchmark comparisons
- `prioridades`: Exactly 5 priorities from the roadmap
- `quick_wins_detail`: 2 items (P1 and P2)
- `transformation_detail`: 3 items (P3, P4, P5)
- `resultados_esperados`: 5-7 before/after metrics
- `proximos_passos`: Exactly 3 next steps

---

## REPORT TO ANALYZE:

{report_content}
