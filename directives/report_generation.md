# Directive: Report Generation

## Goal
Synthesize the audit findings into a professional, actionable report for stakeholders.

## Format
- Primary Output: Markdown file (`final_audit_report.md`).
- Tone: Professional, objective, and evidence-based.

## Structure
1. **Executive Summary**: High-level overview of the system and main findings.
2. **Company Context & Current State**: Baseline understanding of business and operations.
3. **Diagnostic Analysis**: Deep dive into processes, performance, and problems.
4. **Opportunity Assessment**:
   - **Complete Opportunity Backlog**: Comprehensive list of ALL opportunities identified (15-25+ items)
   - Detailed specifications for top 10-15 opportunities
   - Prioritization framework and combined impact projection
5. **Strategic Recommendations & Roadmap**:
   - Top 3-5 priority initiatives with EQUAL depth for each priority
   - Phased implementation roadmap
   - Investment summary and business case

## Tools to Use
- `execution/report_maker.py` (when implemented) to format the Markdown.
- **Prompts**:
    - `prompts/report_executive_summary.md`: To drafting the high-level summary.
    - `prompts/report_full_audit.md`: To generate the body of the report.

## Operating Principles
- Use clear visualizations (tables, lists) where possible.
- Avoid overly technical jargon in the Executive Summary.
- Ensure every "Finding" has a corresponding "Recommendation".
- **Comprehensive Backlog**: List ALL opportunities identified during the audit, not just prioritized ones. This creates a repository for future reference.
- **Consistent Depth**: Maintain equal depth and structure across ALL top priority recommendations. Priority #2, #3, etc. must receive the same comprehensive treatment as Priority #1.
