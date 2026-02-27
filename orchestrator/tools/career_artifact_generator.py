"""
Career Domain Artifact Generator.

Produces:
  - skill_gap_report: markdown table of skill gaps, upskilling path, target roles
  - resume_draft: full ready-to-use resume in markdown (only if resume_analyzer ran)
"""
import json
import time
import uuid
import logging
from gemini_client import generate, is_gemini_response_ok

logger = logging.getLogger(__name__)


def generate_career_artifacts(
    plan: dict,
    tool_results: dict,
    inferred_context: dict,
) -> list[dict]:
    """
    Generate career artifacts from synthesized plan and tool results.

    Args:
        plan: The synthesized plan dict from planner synthesis phase
        tool_results: Dict of tool_name -> result (e.g. resume_analyzer, income_projection)
        inferred_context: Merged extra_context from planner

    Returns:
        List of Artifact dicts ready for SSE emission and memory storage
    """
    artifacts = []
    resume_data = tool_results.get("resume_analyzer", {})
    income_data = tool_results.get("income_projection", {})

    # --- Artifact 1: Skill Gap Report (always generated for career domain) ---
    skill_gap_prompt = f"""You are SHE-ORACLE's Career Document Generator for women professionals in India.

Based on the following strategic analysis, generate a comprehensive Skill Gap Report
formatted as professional markdown.

PLAN SUMMARY: {plan.get('executive_summary', '')}
TARGET ROLE: {inferred_context.get('target_role', 'Not specified')}
LOCATION: {inferred_context.get('location', 'India')}
RESUME ANALYSIS: {json.dumps(resume_data, indent=2)[:1500] if resume_data else 'Not available — use plan context'}
INCOME PROJECTION: {json.dumps(income_data, indent=2)[:600] if income_data else 'Not available'}
SITUATION ANALYSIS: {plan.get('situation_analysis', '')}

Generate a Skill Gap Report with these sections (use markdown headers, be specific and actionable):

# Skill Gap Report

## Current Strengths
[List confirmed strengths as bullet points]

## Critical Skill Gaps
| Skill | Importance | Time to Learn | Best Free Resource |
|-------|-----------|---------------|-------------------|
[3-6 rows with realistic data for India]

## Recommended Upskilling Path
### Phase 1 (Month 1-2): Foundation
### Phase 2 (Month 3-4): Intermediate
### Phase 3 (Month 5-6): Job-Ready

## Target Roles and Expected Salaries (India)
| Role | Entry Salary | 2-Year Salary | Key Requirement |
|------|-------------|---------------|-----------------|
[3-4 rows]

## 90-Day Action Checklist
- [ ] Week 1-2: ...
- [ ] Week 3-4: ...
- [ ] Month 2: ...
- [ ] Month 3: ...

Return ONLY the markdown content — no JSON wrapper, no extra explanation."""

    try:
        skill_gap_text = generate(skill_gap_prompt)
        if is_gemini_response_ok(skill_gap_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "skill_gap_report",
                "title": "Career Skill Gap Analysis Report",
                "domain": "career",
                "content": skill_gap_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {
                    "target_role": inferred_context.get("target_role", ""),
                    "location": inferred_context.get("location", "India"),
                },
            })
    except Exception as e:
        logger.warning(f"Skill gap report generation failed: {e}")

    # --- Artifact 2: Resume Draft (only if resume_analyzer provided data or resume_text given) ---
    resume_text_input = inferred_context.get("resume_text", "")
    has_resume_data = bool(resume_data) or bool(resume_text_input)

    if has_resume_data:
        improvements = resume_data.get("resume_improvements", [])
        strengths = resume_data.get("current_strengths", [])
        target_role = inferred_context.get("target_role", "best-fit role")

        resume_prompt = f"""You are SHE-ORACLE's Resume Writing Specialist for women professionals in India.

Generate a complete, ready-to-use resume in markdown format.

TARGET ROLE: {target_role}
CURRENT PROFILE / RESUME TEXT: {resume_text_input[:800] if resume_text_input else 'Not provided — infer from context below'}
STRENGTHS IDENTIFIED: {json.dumps(strengths) if strengths else 'Derive from plan context'}
IMPROVEMENTS SUGGESTED: {json.dumps(improvements) if improvements else 'Apply industry best practices'}
PLAN CONTEXT: {plan.get('executive_summary', '')}

Generate a complete resume in this markdown format:

# [Professional Name] — [Target Role]
**Location** | **Email** | **LinkedIn** | **Phone**

## Professional Summary
[3 strong sentences: current experience, key achievement with number, target trajectory]

## Core Competencies
[12-16 keywords in 3-4 columns, ATS-optimized for {target_role}]

## Professional Experience
### [Most Recent Role] | [Company] | [City] | [Year–Present]
- [STAR format: achievement with metric]
- [STAR format: achievement with metric]
- [STAR format: achievement with metric]

### [Previous Role] | [Company] | [City] | [Year–Year]
- [Achievement]
- [Achievement]

## Education
### [Degree] | [College/University] | [Year]

## Certifications & Training
- [Relevant certification — free platforms: Coursera, NASSCOM FutureSkills, Google, AWS]

## Key Achievements
1. [Quantified achievement 1]
2. [Quantified achievement 2]
3. [Quantified achievement 3]

---
*Note: Replace bracketed placeholders with your actual information.*

Return ONLY the markdown content."""

        try:
            resume_text = generate(resume_prompt)
            if is_gemini_response_ok(resume_text):
                artifacts.append({
                    "id": str(uuid.uuid4()),
                    "type": "resume_draft",
                    "title": f"Resume Draft — {target_role}",
                    "domain": "career",
                    "content": resume_text.strip(),
                    "format": "markdown",
                    "created_at": time.time(),
                    "metadata": {"target_role": target_role},
                })
        except Exception as e:
            logger.warning(f"Resume draft generation failed: {e}")

    return artifacts
