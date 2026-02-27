"""
Grant Domain Artifact Generator.

Produces:
  - scheme_match_report: per-scheme table with fit score, eligibility, amount
  - scheme_checklist: step-by-step application checklist for top grant
"""
import json
import time
import uuid
import logging
from gemini_client import generate, is_gemini_response_ok

logger = logging.getLogger(__name__)


def generate_grant_artifacts(
    plan: dict,
    tool_results: dict,
    inferred_context: dict,
) -> list[dict]:
    """
    Generate grant artifacts from synthesized plan and tool results.

    Args:
        plan: The synthesized plan dict from planner synthesis phase
        tool_results: Dict including grant_finder result
        inferred_context: Merged extra_context from planner

    Returns:
        List of Artifact dicts (scheme_match_report, scheme_checklist)
    """
    artifacts = []
    grants_data = tool_results.get("grant_finder", {})
    grants = grants_data.get("grants", [])

    # --- Artifact 1: Scheme Match Report ---
    match_prompt = f"""You are SHE-ORACLE's Grant Matching Specialist for women entrepreneurs in India.

Generate a Scheme Match Report.

MATCHING GRANTS FOUND: {json.dumps(grants, indent=2)[:2500] if grants else 'No specific grants found — list top 5 relevant schemes from your knowledge'}
GOAL: {plan.get('goal', '')}
LOCATION: {inferred_context.get('location', 'India')}
BUDGET: {inferred_context.get('budget', 'Not specified')}
PLAN SUMMARY: {plan.get('executive_summary', '')}

Generate a Scheme Match Report in this exact markdown format:

# Grant & Scheme Match Report

## Match Summary
- **Total Schemes Found**: [N]
- **Estimated Total Funding Available**: ₹[amount range]
- **Recommended Application Order**: [Scheme A] → [Scheme B] → [Scheme C]

## Scheme 1 (Best Match): [Scheme Name]
| Field | Details |
|-------|---------|
| **Funding Amount** | ₹[amount] |
| **Type** | Grant / Loan / Subsidy |
| **Administering Body** | [Ministry / Bank / Agency] |
| **Eligibility** | [Key criteria in plain language] |
| **Application Mode** | Online / Offline / Both |
| **Portal / Contact** | [URL or helpline] |
| **Fit Score** | [X]/10 |
| **Why It Fits** | [1-2 sentences] |

## Scheme 2: [Scheme Name]
[Repeat table format]

## Scheme 3: [Scheme Name]
[Repeat table format]

## Application Priority Recommendation
1. **Apply to [Scheme 1] first** because [reason — fastest, highest amount, easiest eligibility]
2. **Then apply to [Scheme 2]** because [reason]
3. **[Scheme 3] as backup** because [reason]

## Combined Funding Potential
If approved for all three schemes: ₹[total] in grants + ₹[total] in subsidized loans

## Grants You May Also Qualify For
- **[Additional scheme]**: [Brief description, link]
- **[Additional scheme]**: [Brief description, link]

Return ONLY the markdown content."""

    try:
        match_text = generate(match_prompt)
        if is_gemini_response_ok(match_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "scheme_match_report",
                "title": "Government Scheme Match Report",
                "domain": "grants",
                "content": match_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {"schemes_found": len(grants)},
            })
    except Exception as e:
        logger.warning(f"Scheme match report generation failed: {e}")

    # --- Artifact 2: Application Checklist ---
    top_grant = grants[0] if grants else {}
    scheme_name = top_grant.get("name", "Top Matching Scheme")

    checklist_prompt = f"""You are SHE-ORACLE's Grant Application Specialist for women in India.

Generate a complete step-by-step Application Checklist.

TOP SCHEME: {json.dumps(top_grant, indent=2) if top_grant else 'PM Mudra Yojana (most common women entrepreneur scheme)'}
GOAL: {plan.get('goal', '')}
LOCATION: {inferred_context.get('location', 'India')}

Generate in this exact markdown format:

# Application Checklist: {scheme_name}

## Phase 1: Gather Documents (Week 1)
- [ ] Aadhaar Card (original + self-attested photocopy)
- [ ] PAN Card
- [ ] Bank account passbook (front page with account details)
- [ ] Passport-size photographs (minimum 4)
- [ ] Proof of business / business idea document
- [ ] Domicile / Residence Certificate
- [ ] Income Certificate from competent authority
- [ ] Caste / Category certificate (if applicable — SC/ST/OBC)
- [ ] [Scheme-specific documents]

## Phase 2: Registration (Week 1-2)
- [ ] Visit official portal: [URL]
- [ ] Create account with mobile number linked to Aadhaar
- [ ] Fill in basic profile (name, address, category)
- [ ] Upload documents (PDF, max 2MB each)
- [ ] Submit and note application / reference number

## Phase 3: Verification (Week 2-4)
- [ ] Respond to any SMS/email queries within 7 days
- [ ] Attend in-person verification if scheduled
- [ ] Submit any additional documents requested

## Phase 4: Follow-Up
- [ ] Check status at [portal] every 7 days
- [ ] Contact helpline if no update after 30 days: [helpline number]
- [ ] Keep all acknowledgement receipts

## Timeline
| Milestone | Expected Date |
|-----------|--------------|
| Documents ready | Week 1 |
| Application submitted | Week 2 |
| Verification complete | Week 4 |
| Approval decision | Week 6–8 |
| Fund disbursement | Week 8–12 |

## Contact for Help
- **Scheme Helpline**: [1800-XXX-XXXX / official helpline]
- **Nearest facilitation centre**: [Type of center + how to find]
- **SHE-ORACLE recommendation**: Visit nearest CSC (Common Service Centre) for free application assistance

Return ONLY the markdown content."""

    try:
        checklist_text = generate(checklist_prompt)
        if is_gemini_response_ok(checklist_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "scheme_checklist",
                "title": f"Application Checklist: {scheme_name}",
                "domain": "grants",
                "content": checklist_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {"scheme_name": scheme_name},
            })
    except Exception as e:
        logger.warning(f"Grant application checklist generation failed: {e}")

    return artifacts
