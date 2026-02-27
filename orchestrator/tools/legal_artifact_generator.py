"""
Legal Domain Artifact Generator.

Produces:
  - rights_summary: applicable laws, rights violated, deadlines, free legal resources
  - escalation_plan: 3-phase escalation with authority contacts and timelines
"""
import json
import time
import uuid
import logging
from gemini_client import generate, is_gemini_response_ok

logger = logging.getLogger(__name__)


def generate_legal_artifacts(
    plan: dict,
    tool_results: dict,
    inferred_context: dict,
) -> list[dict]:
    """
    Generate legal artifacts from synthesized plan and tool results.

    Args:
        plan: The synthesized plan dict from planner synthesis phase
        tool_results: Dict including legal_rights_checker result
        inferred_context: Merged extra_context from planner

    Returns:
        List of Artifact dicts (rights_summary, escalation_plan)
    """
    artifacts = []
    legal_data = tool_results.get("legal_rights_checker", {})
    situation_type = inferred_context.get("situation_type", "workplace")

    # --- Artifact 1: Rights Summary ---
    rights_prompt = f"""You are SHE-ORACLE's Legal Rights Specialist for women in India.

Generate a comprehensive Rights Summary document.

SITUATION TYPE: {situation_type}
USER GOAL / SITUATION: {plan.get('goal', '')}
LEGAL ANALYSIS FROM TOOL: {json.dumps(legal_data, indent=2)[:2000] if legal_data else 'Not available — use your legal knowledge'}
PLAN EXECUTIVE SUMMARY: {plan.get('executive_summary', '')}

Generate a Rights Summary in this exact markdown format:

# Know Your Rights: Legal Protection Summary

## Your Legal Protections
[Which laws apply to your situation and what they guarantee you]
- **[Act Name, Year]** — [What it protects you from, in plain language]
[3-5 applicable laws]

## Rights Violated in Your Case
[Be specific about what violations have occurred, with law citations]
- [Violation 1] — Section [X] of [Act]
- [Violation 2] — Section [Y] of [Act]

## What Your Employer / Perpetrator is Required to Do by Law
- [Legal obligation 1]
- [Legal obligation 2]

## Free Legal Resources Available to You
| Resource | Contact | What They Help With |
|----------|---------|-------------------|
| National Commission for Women (NCW) | 7827170170 | Complaints, legal aid |
| iCall Helpline | 9152987821 | Counseling, legal guidance |
| NALSA (National Legal Services Authority) | 15100 | Free legal representation |
| Cyber Crime Helpline | 1930 | Online harassment |
| Women's Helpline | 181 | Emergency assistance |
[Add any others relevant to the situation]

## Important Deadlines
- **POSH Act Complaint**: Within 3 months of last incident (extendable to 6 months)
- **Labor Court**: Typically within 3 years
- **Criminal Complaint (FIR)**: No limitation period for cognizable offences
- [Any other relevant deadlines for this situation]

## Immediate Protective Steps (Do This Today)
1. [Most urgent step]
2. [Second step]
3. [Third step]

Return ONLY the markdown content."""

    try:
        rights_text = generate(rights_prompt)
        if is_gemini_response_ok(rights_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "rights_summary",
                "title": "Legal Rights Summary",
                "domain": "legal",
                "content": rights_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {"situation_type": situation_type},
            })
    except Exception as e:
        logger.warning(f"Rights summary generation failed: {e}")

    # --- Artifact 2: Escalation Plan ---
    escalation_steps = legal_data.get("escalation_strategy", [])
    helplines = legal_data.get("helplines", [])

    escalation_prompt = f"""You are SHE-ORACLE's Legal Strategy Specialist for women in India.

Generate a detailed step-by-step Legal Escalation Plan.

SITUATION: {plan.get('goal', '')}
ESCALATION STRATEGY FROM ANALYSIS: {json.dumps(escalation_steps, indent=2) if escalation_steps else 'Build from scratch based on situation'}
AVAILABLE HELPLINES: {json.dumps(helplines, indent=2) if helplines else 'Use standard Indian helplines'}
PLAN CONTEXT: {plan.get('situation_analysis', '')}

Generate an Escalation Plan in this exact markdown format:

# Legal Escalation Plan

## Phase 1: Internal Resolution (Week 1–2)
| Action | Authority to Contact | Expected Outcome | Deadline |
|--------|---------------------|-----------------|----------|
| [Action 1] | [Who to contact] | [What should happen] | [Days] |
| [Action 2] | [Who to contact] | [What should happen] | [Days] |

**Documents to Have Ready for Phase 1:**
- [ ] Written complaint (use template below)
- [ ] Evidence log (screenshots, emails, witnesses)
- [ ] [Other specific docs]

## Phase 2: Regulatory / HR Escalation (Day 15–30)
| Action | Authority to Contact | Expected Outcome | Deadline |
|--------|---------------------|-----------------|----------|
| File with POSH Committee / Labor Commissioner | [Specific office] | [Outcome] | Within 30 days |
| [Additional action] | [Authority] | [Outcome] | [Days] |

**Documents to Have Ready for Phase 2:**
- [ ] Phase 1 complaint copy + response (or proof of no response)
- [ ] [Other docs]

## Phase 3: Formal Legal Action (Day 30+)
| Action | Authority to Contact | Expected Outcome | Deadline |
|--------|---------------------|-----------------|----------|
| File FIR / Police Complaint | Local Police Station | FIR registration | Immediate |
| Approach Court / Tribunal | [Specific court] | Legal remedy | [Timeframe] |
| [Other action] | [Authority] | [Outcome] | [Timeline] |

## Authority Contact Directory
| Authority | Address / Contact | Jurisdiction | Hours |
|-----------|-----------------|-------------|-------|
| [Authority 1] | [Contact] | [What they handle] | [Hours] |
[3-5 rows with real Indian authorities]

## Complaint Letter Template
---
To,
[Recipient Designation],
[Organization/Authority Name],
[Address]

Subject: Complaint Regarding [Brief Description]

Respected Sir/Madam,

I, [Your Name], [designation/role] at [organization], wish to bring to your attention the following matter:

[Describe the incident/violation factually with dates]

In view of the above, I request immediate action as per [applicable law/section].

Documents enclosed: [list]

Yours faithfully,
[Name]
[Date]
[Contact]
---

Return ONLY the markdown content."""

    try:
        escalation_text = generate(escalation_prompt)
        if is_gemini_response_ok(escalation_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "escalation_plan",
                "title": "Legal Escalation Plan",
                "domain": "legal",
                "content": escalation_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {"situation_type": situation_type},
            })
    except Exception as e:
        logger.warning(f"Escalation plan generation failed: {e}")

    return artifacts
