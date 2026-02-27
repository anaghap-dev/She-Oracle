"""
Financial Domain Artifact Generator.

Produces:
  - projection_report: 6/12/24 month income projection with growth actions
  - scheme_checklist: government scheme application checklist (if grants found)
"""
import json
import time
import uuid
import logging
from gemini_client import generate, is_gemini_response_ok

logger = logging.getLogger(__name__)


def generate_financial_artifacts(
    plan: dict,
    tool_results: dict,
    inferred_context: dict,
) -> list[dict]:
    """
    Generate financial artifacts from synthesized plan and tool results.

    Args:
        plan: The synthesized plan dict from planner synthesis phase
        tool_results: Dict including income_projection and optionally grant_finder results
        inferred_context: Merged extra_context from planner

    Returns:
        List of Artifact dicts (projection_report, scheme_checklist)
    """
    artifacts = []
    income_data = tool_results.get("income_projection", {})
    grants_data = tool_results.get("grant_finder", {})

    # --- Artifact 1: Income Projection Report ---
    projection_prompt = f"""You are SHE-ORACLE's Financial Planning Specialist for women in India.

Generate a detailed Income Projection Report.

INCOME PROJECTION DATA: {json.dumps(income_data, indent=2)[:2000] if income_data else 'Not available — use plan context and your knowledge'}
CURRENT SKILLS: {inferred_context.get('current_skills', 'Not specified')}
CURRENT INCOME: ₹{inferred_context.get('current_income', 'Not specified')} per annum
LOCATION: {inferred_context.get('location', 'India')}
GOAL: {plan.get('goal', '')}
PLAN SUMMARY: {plan.get('executive_summary', '')}

Generate an Income Projection Report in this exact markdown format:

# Income Projection Report

## Current Financial Position
- **Current Annual Income**: ₹[amount]
- **Domain**: [career/business area]
- **Location Premium**: [city-tier impact on salary]
- **Key Strengths**: [2-3 income-relevant strengths]

## 6-Month Projection
| Action | Income Impact | Confidence | How to Do It |
|--------|--------------|------------|--------------|
| [Action 1] | +₹[amount]/month | High/Medium/Low | [Specific step] |
| [Action 2] | +₹[amount]/month | High/Medium/Low | [Specific step] |
| [Action 3] | +₹[amount]/month | High/Medium/Low | [Specific step] |

**Projected 6-Month Income Range**: ₹[min]–₹[max] per annum

## 12-Month Projection
[Repeat table format for 12-month milestones]

**Projected 12-Month Income Range**: ₹[min]–₹[max] per annum

## 24-Month Financial Independence Milestone
[What financial independence looks like at 24 months, what income level, what savings rate]

**Projected 24-Month Income**: ₹[amount] per annum
**Emergency Fund Target**: ₹[6 months expenses]

## Top 3 High-Value Skills to Add
| Skill | Time to Learn | Cost | Income Boost | Best Free Resource |
|-------|--------------|------|-------------|-------------------|
| [Skill 1] | [Weeks] | Free | +₹[amount]/month | [Resource name + link] |
| [Skill 2] | [Weeks] | Free | +₹[amount]/month | [Resource name + link] |
| [Skill 3] | [Weeks] | Free | +₹[amount]/month | [Resource name + link] |

## Multiple Income Streams Available to You
1. **Primary**: [Current/target job]
2. **Secondary**: [Freelance/consulting opportunity]
3. **Passive**: [Digital product/course/investment]
4. **Government Benefit**: [PM scheme/subsidy you qualify for]

## Immediate Action: Do This This Week
> **[Single most impactful action]** — This one change can add ₹[amount]/month within [timeframe].

Return ONLY the markdown content."""

    try:
        projection_text = generate(projection_prompt)
        if is_gemini_response_ok(projection_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "projection_report",
                "title": "Income Projection Report (6/12/24 Months)",
                "domain": "financial",
                "content": projection_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {
                    "location": inferred_context.get("location", "India"),
                    "current_income": inferred_context.get("current_income", ""),
                },
            })
    except Exception as e:
        logger.warning(f"Projection report generation failed: {e}")

    # --- Artifact 2: Scheme Application Checklist (only if grants found) ---
    grants = grants_data.get("grants", [])
    if grants:
        top_grants = grants[:3]
        checklist_prompt = f"""You are SHE-ORACLE's Government Scheme Application Expert for women in India.

Generate an Application Checklist for the top matching government schemes.

SCHEMES FOUND: {json.dumps(top_grants, indent=2)[:2500]}
GOAL: {plan.get('goal', '')}
LOCATION: {inferred_context.get('location', 'India')}

Generate a Scheme Application Checklist in this exact markdown format:

# Government Scheme Application Checklist

## Common Documents to Prepare First (Required for All Applications)
- [ ] Aadhaar Card (original + self-attested copy)
- [ ] PAN Card
- [ ] Bank account details (passbook front page / cancelled cheque)
- [ ] Passport-size photographs (6 copies)
- [ ] Domicile / Residence Certificate
- [ ] Income Certificate from Tehsildar
- [ ] Caste Certificate (if applicable)

## Priority Scheme 1: [Scheme Name from data]
**Amount**: [Amount]
**Deadline**: [Application deadline or rolling]
**Portal**: [URL]

### Documents Required
- [ ] [Scheme-specific document 1]
- [ ] [Scheme-specific document 2]

### Application Steps
1. Visit [portal/office]
2. [Step 2]
3. [Step 3]
4. Submit and collect acknowledgement
5. Follow up after [X] days

### Processing Time
[Typical processing time]

## Priority Scheme 2: [Next Scheme]
[Repeat same structure]

## Priority Scheme 3: [Next Scheme]
[Repeat same structure]

## Online Application Tips
- Register at **pmvishwakarma.gov.in** or **nsdc.in** for skill-linked schemes
- Use **JAM trinity** (Jan Dhan + Aadhaar + Mobile) for instant benefit transfer
- Track application status at **pfms.nic.in**

## After Applying: What to Expect
1. SMS/email acknowledgement within [X] days
2. Verification visit / document check
3. Approval / disbursement within [Y] days

Return ONLY the markdown content."""

        try:
            checklist_text = generate(checklist_prompt)
            if is_gemini_response_ok(checklist_text):
                artifacts.append({
                    "id": str(uuid.uuid4()),
                    "type": "scheme_checklist",
                    "title": "Government Scheme Application Checklist",
                    "domain": "financial",
                    "content": checklist_text.strip(),
                    "format": "markdown",
                    "created_at": time.time(),
                    "metadata": {"schemes_found": len(grants)},
                })
        except Exception as e:
            logger.warning(f"Scheme checklist generation failed: {e}")

    return artifacts
