# Directive: Presentation Generation

## Goal
Transform the approved Final Audit Report into a professional 15-slide executive PPTX presentation.

## Prerequisites
- Final Audit Report (`AI Audit/Final Audit Report.md`) is completed and approved.
- Python environment with `python-pptx` installed.

## Workflow

### Step 1: Data Extraction
Use the prompt template at `prompts/presentation_data_extraction.md` to extract structured JSON data from the Final Audit Report.

**Process:**
1. Read the full `AI Audit/Final Audit Report.md`.
2. Feed the report content into the extraction prompt template (replacing `{report_content}`).
3. The LLM should return a single JSON object following the defined schema.
4. Save the output as `.tmp/presentation_data.json` in the client folder.

**Validation:**
- JSON must be valid and parseable.
- All required fields must be present.
- `client_name` must match the actual client.
- Exactly 3 KPIs, 3 discoveries, 5 priorities, 3 next steps.

### Step 2: PPTX Generation
Run the presentation maker script:

```bash
python execution/presentation_maker.py \
  --data "[Client Folder]/.tmp/presentation_data.json" \
  --output "[Client Folder]/AI Audit/AI Audit — [Client Name] — Apresentação.pptx"
```

### Step 3: Quality Review
Open the generated PPTX and verify:

- [ ] 15 slides total
- [ ] Slide 1: Client name correct, "AI Audit" title visible
- [ ] Slide 2: Agenda has 4 time blocks
- [ ] Slide 3: 3 KPI cards with correct values
- [ ] Slide 4: 3 discovery summary cards
- [ ] Slides 5-7: Discovery details with metrics/quotes/flow
- [ ] Slide 8: 3 big impact numbers (dark background)
- [ ] Slide 9: Benchmark table (5 rows x 5 columns)
- [ ] Slide 10: 5 priority columns with ROI/payback/timeline
- [ ] Slide 11: P1 & P2 quick win detail cards
- [ ] Slide 12: P3, P4, P5 transformation detail cards
- [ ] Slide 13: ROI consolidated (4 cards, dark background)
- [ ] Slide 14: Results table (before/after metrics)
- [ ] Slide 15: 3 next steps with timeline badges
- [ ] All text in Portuguese (pt-BR)
- [ ] No text overflow or truncation
- [ ] Color coding consistent (green=positive, red=critical, amber=caution, blue=neutral)

## Output
- `AI Audit/AI Audit — [Client Name] — Apresentação.pptx` in the client's `AI Audit/` subfolder.

## Design Reference
The PPTX follows the established AI Audit presentation template with:
- 16:9 widescreen (10" x 5.625")
- Calibri font throughout
- Dark/light slide alternation
- Color-coded cards and accent bars
- All visuals built from shapes (no native charts/tables)
