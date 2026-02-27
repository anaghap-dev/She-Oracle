"""
Tool: risk_assessment
Evaluates business or career plans for risks across financial,
legal, market, and operational dimensions with mitigation strategies.
"""
import json
from gemini_client import generate


def risk_assessment(plan: str, plan_type: str = "business", budget: str = "") -> dict:
    """
    Assess risks in a business or career plan.

    Args:
        plan: Description of the business/career plan
        plan_type: One of 'business', 'career', 'investment', 'startup'
        budget: Available budget or investment amount

    Returns:
        dict with risk matrix, mitigation strategies, go/no-go recommendation
    """
    prompt = f"""You are SHE-ORACLE's Risk Intelligence Agent — an expert in evaluating business and career risks for women entrepreneurs and professionals in India.

Plan Description: {plan}
Plan Type: {plan_type}
Available Budget: {budget if budget else "Not specified"}

Conduct a comprehensive risk assessment as JSON.

Return ONLY valid JSON in this exact format:
{{
  "overall_risk_level": "High/Medium/Low",
  "overall_feasibility_score": 7,
  "go_no_go": "GO/CONDITIONAL GO/NO GO",
  "go_no_go_reasoning": "2-3 sentence explanation",
  "risk_matrix": [
    {{
      "category": "Financial",
      "risk": "Specific risk description",
      "probability": "High/Medium/Low",
      "impact": "High/Medium/Low",
      "risk_score": 8,
      "mitigation": "Specific mitigation strategy",
      "contingency": "What to do if this risk materializes"
    }},
    {{
      "category": "Legal/Regulatory",
      "risk": "Specific risk",
      "probability": "Medium",
      "impact": "High",
      "risk_score": 6,
      "mitigation": "Mitigation strategy",
      "contingency": "Contingency plan"
    }},
    {{
      "category": "Market",
      "risk": "Market risk",
      "probability": "Medium",
      "impact": "Medium",
      "risk_score": 5,
      "mitigation": "Mitigation",
      "contingency": "Contingency"
    }},
    {{
      "category": "Operational",
      "risk": "Operational risk",
      "probability": "Low",
      "impact": "Medium",
      "risk_score": 4,
      "mitigation": "Mitigation",
      "contingency": "Contingency"
    }}
  ],
  "women_specific_risks": [
    {{
      "risk": "Risk specific to women entrepreneurs/professionals",
      "mitigation": "How to address this"
    }}
  ],
  "critical_success_factors": [
    "Factor that must go right for success"
  ],
  "minimum_viable_version": "Smallest version of this plan that can be executed to test viability",
  "recommended_timeline": {{
    "phase1": "What to do first and duration",
    "phase2": "Second phase",
    "phase3": "Third phase"
  }},
  "exit_strategy": "If this doesn't work, here's how to exit with minimal loss"
}}"""

    text = generate(prompt)

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "overall_risk_level": "Unknown",
            "overall_feasibility_score": 5,
            "go_no_go": "CONDITIONAL GO",
            "go_no_go_reasoning": text,
            "risk_matrix": [],
            "women_specific_risks": [],
            "critical_success_factors": [],
            "minimum_viable_version": "",
            "recommended_timeline": {},
            "exit_strategy": "",
        }
