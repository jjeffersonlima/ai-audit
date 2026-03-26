# Directive: AI Audit Workflow

## Goal
Coordinate a full AI Audit from start to finish. This directive ensures that all necessary data is collected, risks are analyzed, and a final report is generated.

## Workflow Steps

1. **Step 1: Data Collection & Contextualization**
   - Goal: Gather all necessary information about the AI system.
   - Component: `directives/data_collection.md`
   - Output: `data_package.json` in `.tmp/`

2. **Step 2: Process Analysis**
   - Goal: Identify automation opportunities and ROI.
   - Component: `directives/process_analysis.md`
   - Input: `data_package.json`
   - Output: `process_findings.json` in `.tmp/`

3.  **Step 3: Risk & Compliance Assessment**
   - Goal: Evaluate the system against ethical, legal, and safety standards.
   - Component: `directives/risk_assessment.md`
   - Input: `data_package.json`
   - Output: `risk_findings.json` in `.tmp/`

4. **Step 4: Report Synthesis**
   - Goal: Transform technical findings into a professional audit report.
   - Component: `directives/report_generation.md`
   - Input: `risk_findings.json`
   - Output: `AI Audit/Final Audit Report.md`

5. **Step 5: Presentation Generation**
   - Goal: Transform the approved final report into a professional executive PPTX presentation.
   - Component: `directives/presentation_generation.md`
   - Input: `AI Audit/Final Audit Report.md`
   - Output: `AI Audit/AI Audit — [Client Name] — Apresentação.pptx`
   - Script: `execution/presentation_maker.py`
   - Prompt: `prompts/presentation_data_extraction.md`
   - **Trigger:** Only after the Final Audit Report is reviewed and approved.

## Operating Instructions
- LLM (Orchestrator) must read each sub-directive before proceeding to the next step.
- All intermediate data must be stored in `.tmp/` to maintain the 3-layer separation.
- If a step fails, the Orchestrator should attempt to self-anneal or ask for missing information.
