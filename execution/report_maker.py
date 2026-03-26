import json
import os
from datetime import datetime
from typing import Dict, Any

def generate_report(findings: Dict[str, Any], data_package: Dict[str, Any]) -> str:
    """
    Constructs a Markdown report from findings and data package.
    """
    sys_name = data_package.get("system_overview", {}).get("name", "Unknown System")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# AI Audit Report: {sys_name}
Date: {date_str}

## 1. Executive Summary
This report summarizes the findings of the AI Audit conducted for the {sys_name} system. The audit focused on compliance, bias, and technical robustness.

**Overall Compliance Score: {findings.get('compliance_score', 'N/A')}%**

## 2. Risk Matrix
| Area | Risk | Impact | Likelihood |
|------|------|--------|------------|
"""
    for item in findings.get("risk_matrix", []):
        report += f"| {item['area']} | {item['risk']} | {item['impact']} | {item['likelihood']} |\n"

    report += """
## 3. Mitigation Strategies
The following actions are recommended to address identified risks:
"""
    for strategy in findings.get("mitigation_strategies", []):
        report += f"- {strategy}\n"

    report += """
## 4. Conclusion
The audit process is complete. Further continuous monitoring is advised as the system evolves.
"""
    return report

def load_json(filepath: str) -> Dict:
    with open(filepath, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    try:
        findings = load_json(".tmp/risk_findings.json")
        data = load_json(".tmp/data_package.json")
        
        report_md = generate_report(findings, data)
        
        output_path = "final_audit_report.md"
        with open(output_path, "w") as f:
            f.write(report_md)
        print(f"Report generated successfully: {output_path}")
    except Exception as e:
        print(f"Error generating report: {e}")
