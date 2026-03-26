# Directive: Process Analysis

## Goal
Analyze interview transcripts to map business processes, identify inefficiencies, and calculate ROI.

## Inputs
- **Team Interview Transcripts**: Raw text from interviews with SDRs, BDRs, etc.
- **Kickoff Data**: Context from the first phase.

## Tools to Use
- **Prompts**:
    - `prompts/process_bottleneck_analysis.md`: For detailed analysis of single processes.
    - `prompts/process_quick_wins.md`: For finding low-hanging fruit across multiple processes.
    - `prompts/process_roi_calculator.md`: For quantifying the value of automation.

## Workflow
1. **Map Processes**: Extract step-by-step workflows from **Team Interview Transcripts**.
2. **Identify Candidates**: Review mapped processes to find labor-intensive areas.
3. **Analyze Bottlenecks**: Run `process_bottleneck_analysis.md` for high-priority processes.
3. **Find Quick Wins**: Run `process_quick_wins.md` to show immediate value.
4. **Calculate ROI**: For the most promising opportunities, use `process_roi_calculator.md` to estimate savings.

## Output
- `.tmp/process_analysis_findings.json` containing:
    - List of analyzed processes.
    - Identified bottlenecks and recommended tools.
    - ROI projections.
