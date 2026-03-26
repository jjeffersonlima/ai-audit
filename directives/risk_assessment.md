# Directive: Risk Assessment

## Goal
Analyze the AI system for potential risks, biases, and compliance gaps based on the collected data.

## Criteria
1. **Bias & Fairness**: Does the model show discriminatory patterns?
2. **Robustness & Safety**: Is the system resilient to adversarial inputs or edge cases?
3. **Transparency & Explainability**: Can the system's decisions be understood?
4. **Data Privacy**: Is personal data handled according to regulations?

## Tools to Use
- `execution/analyzer.py` (when implemented) to run specific evaluation patterns.

## Output
- `.tmp/risk_findings.json` including:
    - `risk_matrix`: List of identified risks, impact, and likelihood.
    - `compliance_score`: Percentage alignment with target regulations.
    - `mitigation_strategies`: Recommended actions for each risk.

## Instructions
- Reference specific clauses of the EU AI Act or other relevant frameworks provided in the context.
- Prioritize high-impact risks that could lead to legal or ethical failures.
