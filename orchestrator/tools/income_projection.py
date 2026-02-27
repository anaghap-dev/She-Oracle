"""
Tool: income_projection
Projects income trajectories based on current skills, upskilling path,
and location. Builds 6/12/24 month financial forecasts.
"""
import json
from gemini_client import generate


def income_projection(
    current_skills: str,
    current_income: str = "0",
    target_domain: str = "",
    location: str = "India",
    education_level: str = "Graduate",
) -> dict:
    """
    Project income across multiple time horizons.

    Args:
        current_skills: Comma-separated list of current skills or skill description
        current_income: Current monthly/annual income (string with amount)
        target_domain: Target industry or domain
        location: City or region in India
        education_level: Highest education qualification

    Returns:
        dict with income projections, skill-income mapping, action plan
    """
    prompt = f"""You are SHE-ORACLE's Financial Intelligence Agent — an expert in income planning and financial independence for women in India.

Current Profile:
- Skills: {current_skills}
- Current Income: {current_income}
- Target Domain: {target_domain if target_domain else "Best fit based on skills"}
- Location: {location}
- Education: {education_level}

Create a detailed income projection and financial independence roadmap as JSON.

Return ONLY valid JSON in this exact format:
{{
  "current_income_assessment": {{
    "estimated_current_monthly": "Amount in INR",
    "market_benchmark": "What someone with these skills typically earns",
    "gap_analysis": "How far current income is from market rate"
  }},
  "income_projections": [
    {{
      "timeline": "6 months",
      "projected_monthly_income": "Amount in INR",
      "projected_annual_income": "Amount in INR",
      "key_actions_required": ["Action1", "Action2"],
      "skills_to_add": ["Skill1"],
      "confidence_level": "High/Medium/Low"
    }},
    {{
      "timeline": "12 months",
      "projected_monthly_income": "Amount in INR",
      "projected_annual_income": "Amount in INR",
      "key_actions_required": ["Action1", "Action2"],
      "skills_to_add": ["Skill1"],
      "confidence_level": "High/Medium/Low"
    }},
    {{
      "timeline": "24 months",
      "projected_monthly_income": "Amount in INR",
      "projected_annual_income": "Amount in INR",
      "key_actions_required": ["Action1", "Action2"],
      "skills_to_add": ["Skill1"],
      "confidence_level": "High/Medium/Low"
    }}
  ],
  "high_value_skills": [
    {{
      "skill": "Skill name",
      "income_boost_percent": "30%",
      "time_to_learn": "2 months",
      "free_resource": "Specific free course/resource"
    }}
  ],
  "multiple_income_streams": [
    {{
      "stream": "Income stream name",
      "type": "Active/Passive/Semi-passive",
      "estimated_monthly": "Amount",
      "startup_effort": "Low/Medium/High",
      "how_to_start": "Specific steps"
    }}
  ],
  "financial_independence_milestone": {{
    "target_monthly_expenses": "Estimated for {location}",
    "financial_independence_income": "Amount needed monthly",
    "estimated_years_to_fi": "X years",
    "key_milestones": ["Milestone 1", "Milestone 2"]
  }},
  "government_benefits_to_claim": [
    "Specific benefit or scheme relevant to income level"
  ],
  "immediate_action": "The single most impactful thing to do this week"
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
            "current_income_assessment": {},
            "income_projections": [],
            "high_value_skills": [],
            "multiple_income_streams": [],
            "financial_independence_milestone": {},
            "government_benefits_to_claim": [],
            "immediate_action": text,
        }
