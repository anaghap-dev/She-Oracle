"""
Education Domain Artifact Generator.

Produces:
  - scholarship_list: markdown table of matching scholarships with amount, eligibility, portal
  - enrollment_checklist: docs required + NSP registration steps + application calendar
"""
import json
import time
import uuid
import logging
from gemini_client import generate, is_gemini_response_ok

logger = logging.getLogger(__name__)


def generate_education_artifacts(
    plan: dict,
    tool_results: dict,
    inferred_context: dict,
) -> list[dict]:
    """
    Generate education artifacts from synthesized plan and tool results.

    Args:
        plan: The synthesized plan dict from planner synthesis phase
        tool_results: Dict including grant_finder result (used for scholarships)
        inferred_context: Merged extra_context from planner

    Returns:
        List of Artifact dicts (scholarship_list, enrollment_checklist)
    """
    artifacts = []
    grants_data = tool_results.get("grant_finder", {})
    grants = grants_data.get("grants", [])

    # --- Artifact 1: Scholarship Match List ---
    scholarship_prompt = f"""You are SHE-ORACLE's Education Opportunity Specialist for women in India.

Generate a comprehensive Scholarship Match List.

MATCHING SCHOLARSHIPS / SCHEMES FOUND: {json.dumps(grants, indent=2)[:2000] if grants else 'Not available — list top relevant scholarships from your knowledge'}
GOAL: {plan.get('goal', '')}
LOCATION: {inferred_context.get('location', 'India')}
PLAN SUMMARY: {plan.get('executive_summary', '')}

Generate a Scholarship Match List in this exact markdown format:

# Scholarship Match List

## Top Scholarships for You

| Scholarship | Amount (Annual) | Eligibility | Deadline | Apply At |
|-------------|----------------|-------------|----------|----------|
| [Scholarship 1] | ₹[amount] | [Key criteria] | [Month/Rolling] | [Portal URL] |
| [Scholarship 2] | ₹[amount] | [Key criteria] | [Month/Rolling] | [Portal URL] |
| [Scholarship 3] | ₹[amount] | [Key criteria] | [Month/Rolling] | [Portal URL] |
| [Scholarship 4] | ₹[amount] | [Key criteria] | [Month/Rolling] | [Portal URL] |
| [Scholarship 5] | ₹[amount] | [Key criteria] | [Month/Rolling] | [Portal URL] |

*Priority: Apply to all via [scholarships.gov.in](https://scholarships.gov.in) (National Scholarship Portal)*

## Free Education Programs
| Program | Provider | Duration | Certificate | Link |
|---------|----------|----------|-------------|------|
| PMKVY (Skill Training) | NSDC | 3-6 months | Yes | pmkvyofficial.org |
| Google Career Certificates | Google / Coursera | 3-6 months | Yes | grow.google/intl/en_in |
| AWS Educate | Amazon | Self-paced | Yes | aws.amazon.com/training |
| NASSCOM FutureSkills | NASSCOM | Self-paced | Yes | futureskills.nasscom.in |
| Swayam MOOC Courses | MHRD | Self-paced | Yes | swayam.gov.in |

## Skill Development Grants
- **PMKVY (Pradhan Mantri Kaushal Vikas Yojana)**: Free training + ₹8,000 stipend for women in priority sectors
- **DDU-GKY**: Free residential training for rural women with 100% job placement support
- **SANKALP**: World Bank-funded skill development with stipend

## Application Tips for Maximum Success
1. **Apply early** — most scholarships close by August-September for academic year
2. **Use one portal** — National Scholarship Portal (scholarships.gov.in) covers 100+ central schemes
3. **Bank account in your name** — mandatory for direct benefit transfer
4. **Keep income certificate updated** — most require certificate not older than 6 months
5. **Apply to multiple schemes** — there is no rule against receiving multiple scholarships

## Scholarship Portal Quick Reference
| Portal | Covers | URL |
|--------|--------|-----|
| National Scholarship Portal | 100+ Central Govt Scholarships | scholarships.gov.in |
| State Scholarship Portal | State-specific scholarships | [your state].gov.in |
| Buddy4Study | Private scholarships | buddy4study.com |
| Vidyasaarathi | Corporate CSR scholarships | vidyasaarathi.co.in |

Return ONLY the markdown content."""

    try:
        scholarship_text = generate(scholarship_prompt)
        if is_gemini_response_ok(scholarship_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "scholarship_list",
                "title": "Scholarship Match List",
                "domain": "education",
                "content": scholarship_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {"location": inferred_context.get("location", "India")},
            })
    except Exception as e:
        logger.warning(f"Scholarship list generation failed: {e}")

    # --- Artifact 2: Enrollment Checklist ---
    enroll_prompt = f"""You are SHE-ORACLE's Education Application Specialist for women in India.

Generate a complete Enrollment and Application Checklist for government scholarships.

GOAL: {plan.get('goal', '')}
LOCATION: {inferred_context.get('location', 'India')}
ROADMAP FROM PLAN: {json.dumps(plan.get('roadmap', []), indent=2)[:800] if plan.get('roadmap') else 'Not available'}

Generate in this exact markdown format:

# Scholarship Enrollment Checklist

## Documents to Gather (Collect All Before Applying)
- [ ] Aadhaar Card (mandatory — link to mobile number)
- [ ] Bank account in your own name (not joint) with IFSC code
- [ ] Latest academic marksheets / certificates (all years)
- [ ] Bonafide Certificate from current institution
- [ ] Income Certificate from Tehsildar / SDM (not older than 6 months)
- [ ] Caste / Category Certificate from competent authority (if SC/ST/OBC/EWS)
- [ ] Domicile Certificate
- [ ] Passport-size photographs (6-8 copies)
- [ ] Fee receipt from current institution
- [ ] Disability Certificate (if applicable)

## National Scholarship Portal (NSP) Registration Steps
1. Go to [scholarships.gov.in](https://scholarships.gov.in)
2. Click "New Registration" under Student Login
3. Fill in: State, Academic Year, Scheme Type, Name as on Aadhaar, Date of Birth, Gender, Mobile Number (linked to Aadhaar), Bank Account Number, IFSC Code, Identity Number (Aadhaar)
4. Note down your Application ID and Password
5. Log in and complete your full profile
6. Apply for eligible scholarships (multiple can be selected)
7. Upload all documents (PDF, max 500KB each)
8. Submit and print acknowledgement

## Application Deadlines Calendar
| Month | Action |
|-------|--------|
| June–July | Collect and update all documents |
| August | Open NSP registration; apply early for pre-matric schemes |
| September | Last date for most post-matric schemes |
| October–November | State scholarship deadlines (check state portal) |
| December–January | Private / corporate scholarship deadlines |
| Rolling (any time) | PMKVY, Swayam courses, skill development programs |

## After Applying: What to Expect
1. **Acknowledgement SMS** within 1-2 days
2. **Institute verification** — your institution must approve your application within 30 days
3. **State/Central verification** — 30-60 days
4. **Approval notification** via SMS and portal
5. **Disbursement** directly to your bank account (typically within 90 days of application)

## Troubleshooting
- **Aadhaar not linked to mobile?** Visit nearest Aadhaar centre (free service)
- **Bank account in parent's name?** Open a zero-balance Jan Dhan account at any bank (free, same day)
- **Institution not registered on NSP?** Ask principal to register at NSP — it's mandatory for students to apply
- **Application rejected?** Check reason on portal and re-apply with corrected documents

## Free Help Centers
- **Common Service Centres (CSC)**: Free scholarship application help — find nearest at locator.csccloud.in
- **State Scholarship Cell**: [State education dept contact]
- **NSP Helpdesk**: 0120-6619540 | helpdesk@nsp.gov.in

Return ONLY the markdown content."""

    try:
        enroll_text = generate(enroll_prompt)
        if is_gemini_response_ok(enroll_text):
            artifacts.append({
                "id": str(uuid.uuid4()),
                "type": "enrollment_checklist",
                "title": "Scholarship Enrollment Checklist",
                "domain": "education",
                "content": enroll_text.strip(),
                "format": "markdown",
                "created_at": time.time(),
                "metadata": {"location": inferred_context.get("location", "India")},
            })
    except Exception as e:
        logger.warning(f"Enrollment checklist generation failed: {e}")

    return artifacts
