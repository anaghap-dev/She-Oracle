"""
Tool: resume_analyzer
Analyzes resume text for skill gaps, market positioning,
and generates an upskilling roadmap with job targets.
"""
import json
from gemini_client import generate


def resume_analyzer(resume_text: str, target_role: str = "", location: str = "India") -> dict:
    """
    Analyze a resume and return skill gap analysis with roadmap.

    Args:
        resume_text: Raw text of the resume (or description of current skills/experience)
        target_role: Desired job role or career goal
        location: Target job market location

    Returns:
        dict with skill gaps, strengths, roadmap, job targets, salary expectations
    """
    prompt = f"""You are SHE-ORACLE's Career Intelligence Agent — an expert career strategist for women professionals in India.

Resume / Current Skills Profile:
{resume_text}

Target Role: {target_role if target_role else "Best fit role based on profile"}
Location: {location}

Provide a comprehensive career analysis as JSON.

Return ONLY valid JSON in this exact format:
{{
  "current_strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "skill_gaps": [
    {{
      "skill": "Missing skill name",
      "importance": "Critical/High/Medium",
      "reason": "Why this skill matters for target role",
      "learning_resource": "Specific free/paid resource to learn it",
      "time_to_learn": "Estimated weeks/months"
    }}
  ],
  "recommended_roles": [
    {{
      "title": "Job title",
      "fit_score": 8,
      "avg_salary_lpa": "X-Y LPA",
      "top_companies": ["Company1", "Company2"],
      "required_skills": ["Skill1", "Skill2"]
    }}
  ],
  "upskilling_roadmap": [
    {{
      "phase": 1,
      "duration": "Month 1-2",
      "focus": "What to learn",
      "resources": ["Resource1", "Resource2"],
      "milestone": "What you should be able to do"
    }}
  ],
  "resume_improvements": [
    "Specific improvement suggestion"
  ],
  "women_specific_opportunities": [
    "Women-specific job boards, programs, or initiatives relevant to this profile"
  ],
  "networking_strategy": "Specific networking advice for this profile and location",
  "timeline_to_target_role": "Realistic timeline estimate"
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
            "current_strengths": [],
            "skill_gaps": [],
            "recommended_roles": [],
            "upskilling_roadmap": [],
            "resume_improvements": [text],
            "women_specific_opportunities": [],
            "networking_strategy": "",
            "timeline_to_target_role": "",
        }
