"""
Tool: document_generator
Generates formal legal documents for digital harassment cases:
- FIR draft (First Information Report)
- Formal complaint letter to Cyber Cell
- Platform takedown request
- Legal notice to harasser
"""
import json
from datetime import date
from gemini_client import generate


def generate_documents(
    victim_name: str,
    incident_description: str,
    evidence_summary: str,
    threat_analysis: dict,
    contact_info: str = "",
) -> dict:
    """
    Generate formal documents for filing a digital harassment case.

    Args:
        victim_name: Name of the complainant (use "Complainant" if anonymous)
        incident_description: Description of what happened (in victim's words)
        evidence_summary: Summary of collected digital evidence
        threat_analysis: Output from threat_analyzer tool
        contact_info: Optional contact details for official documents

    Returns:
        dict with: fir_draft, complaint_letter, takedown_request, legal_notice, document_tips
    """
    today = date.today().strftime("%d/%m/%Y")
    threat_type = threat_analysis.get("threat_classification", {}).get("primary_type", "online harassment")
    severity_level = threat_analysis.get("severity", {}).get("level", "MODERATE")
    severity_score = threat_analysis.get("severity", {}).get("score", 5)

    legal_sections = threat_analysis.get("legal_mapping", {}).get("primary_sections", [])
    sections_text = ", ".join(
        [f"{s.get('act')} {s.get('section')}" for s in legal_sections]
    ) if legal_sections else "Section 66C/66E IT Act 2000, Section 354D IPC"

    cognizable = threat_analysis.get("legal_mapping", {}).get("cognizable_offence", True)

    prompt = f"""You are a legal document drafting assistant specializing in Indian cyber law.
Generate formal documents for a digital harassment case.

CASE DETAILS:
- Complainant: {victim_name}
- Date: {today}
- Incident Type: {threat_type}
- Severity: {severity_level} ({severity_score}/10)
- Incident Description: {incident_description}
- Evidence Available: {evidence_summary}
- Applicable Legal Sections: {sections_text}
- Cognizable Offence: {cognizable}

Generate ALL FOUR documents. Return ONLY valid JSON:

{{
  "fir_draft": {{
    "title": "FIRST INFORMATION REPORT (DRAFT)",
    "content": "Complete FIR text ready to submit at police station. Should include: complainant details section, incident date/time section, detailed description of offence, evidence particulars, accused details (if known), relief sought, signature section. Use formal Indian police FIR language. Include placeholders like [DATE], [TIME], [POLICE STATION] where user needs to fill in. Minimum 300 words."
  }},
  "complaint_letter": {{
    "title": "COMPLAINT TO CYBER CRIME CELL",
    "content": "Formal letter addressed to the Superintendent of Police (Cyber Crime Cell). Should reference specific IT Act sections, describe the offence clearly, list evidence, state the relief sought. Professional legal language. Include all standard letter components. Minimum 250 words."
  }},
  "takedown_request": {{
    "title": "PLATFORM CONTENT REMOVAL REQUEST",
    "content": "Formal email/letter to platform (with [PLATFORM NAME] placeholder) requesting content removal. Should cite Section 79 IT Act (intermediary liability), specific sections violated, describe content clearly, provide evidence links/details, demand timeline for removal, state consequences of non-compliance. Professional tone. Minimum 200 words."
  }},
  "legal_notice": {{
    "title": "LEGAL NOTICE TO ACCUSED",
    "content": "Formal legal notice under Section 80 CPC to the accused (with [ACCUSED NAME/UNKNOWN] placeholder). Should demand immediate cessation of harassment, acknowledgment of legal violations, destruction of any intimate content, and state that non-compliance will result in criminal prosecution and civil suit. Attorney-level language. Minimum 200 words."
  }},
  "document_tips": [
    "Tip 1 for using these documents effectively",
    "Tip 2",
    "Tip 3",
    "Tip 4"
  ]
}}"""

    text = generate(prompt)

    # Strip markdown fences
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Return template fallback
        return {
            "fir_draft": {
                "title": "FIRST INFORMATION REPORT (DRAFT)",
                "content": _fir_template(victim_name, incident_description, sections_text, today),
            },
            "complaint_letter": {
                "title": "COMPLAINT TO CYBER CRIME CELL",
                "content": _complaint_template(victim_name, incident_description, sections_text, today),
            },
            "takedown_request": {
                "title": "PLATFORM CONTENT REMOVAL REQUEST",
                "content": _takedown_template(incident_description, sections_text, today),
            },
            "legal_notice": {
                "title": "LEGAL NOTICE TO ACCUSED",
                "content": _legal_notice_template(victim_name, sections_text, today),
            },
            "document_tips": [
                "Print the FIR draft and present it at your local police station or cyber cell.",
                "Police cannot refuse to register an FIR for cognizable offences — insist on registration.",
                "Keep a copy of all documents submitted and get acknowledgment receipts.",
                "For online complaints, save the complaint number from cybercrime.gov.in.",
            ],
        }


def _fir_template(name, description, sections, today):
    return f"""TO,
The Station House Officer,
[POLICE STATION NAME], [CITY]
Pin: [PINCODE]

SUBJECT: First Information Report regarding Cyber Crime / Online Harassment

Date: {today}

Sir/Madam,

I, {name}, resident of [ADDRESS], hereby lodge this First Information Report regarding a cyber crime committed against me.

INCIDENT DETAILS:
Date of Incident: [DATE OF INCIDENT]
Time: [TIME]
Nature of Offence: Online Harassment / Cyber Crime

DESCRIPTION OF INCIDENT:
{description}

EVIDENCE IN MY POSSESSION:
[List your screenshots, URLs, saved messages here]

APPLICABLE LEGAL SECTIONS:
The above acts constitute offences punishable under {sections}.

RELIEF SOUGHT:
1. Registration of FIR and initiation of investigation.
2. Identification and arrest of the accused.
3. Preservation of digital evidence.
4. Protection from further harassment.

I solemnly declare that the information given above is true and correct to the best of my knowledge.

Yours faithfully,
{name}
Contact: [YOUR PHONE NUMBER]
Date: {today}
Place: [YOUR CITY]"""


def _complaint_template(name, description, sections, today):
    return f"""To,
The Superintendent of Police,
Cyber Crime Cell, [CITY]
[ADDRESS]

Subject: Complaint regarding Online Harassment / Cyber Crime

Date: {today}
Reference: Complaint under {sections}

Respected Sir/Madam,

I, {name}, residing at [ADDRESS], am writing to report a serious cyber crime that has been perpetrated against me.

NATURE OF COMPLAINT:
{description}

LEGAL VIOLATIONS:
The actions of the accused constitute offences under {sections} of the Information Technology Act, 2000 and the Indian Penal Code.

EVIDENCE:
I am attaching the following evidence: [LIST YOUR EVIDENCE - screenshots, URLs, message logs]

RELIEF REQUESTED:
1. Register my complaint and initiate a formal investigation.
2. Issue notice to the platform(s) involved for preservation and disclosure of data.
3. Take appropriate legal action against the accused.

I am available for any further information or questioning.

Yours sincerely,
{name}
Phone: [YOUR PHONE]
Email: [YOUR EMAIL]
Date: {today}"""


def _takedown_template(description, sections, today):
    return f"""To,
The Grievance Officer,
[PLATFORM NAME] — Trust & Safety Department
[PLATFORM EMAIL / SUPPORT URL]

Subject: Formal Request for Content Removal — Violation of Indian IT Act

Date: {today}

Dear Grievance Officer,

I am writing to formally request the immediate removal of content that violates Indian law and your platform's Terms of Service.

CONTENT TO BE REMOVED:
URL/Link: [PASTE URL HERE]
Type of Content: [DESCRIBE CONTENT]
Date First Noticed: [DATE]

LEGAL BASIS FOR REMOVAL:
This content violates {sections} of the Information Technology Act, 2000 (India). Under Section 79(3)(b) of the IT Act, you are required to expeditiously remove this content upon receiving actual knowledge of its unlawfulness.

NATURE OF VIOLATION:
{description}

I request:
1. Immediate removal of the above content.
2. Preservation of all associated account data for law enforcement purposes.
3. Written confirmation of removal within 48 hours.

Non-compliance with this request may result in the platform losing its intermediary liability protection under Section 79 of the IT Act.

Regards,
[YOUR NAME]
[YOUR CONTACT]
Date: {today}"""


def _legal_notice_template(name, sections, today):
    return f"""LEGAL NOTICE

To,
[ACCUSED NAME / UNKNOWN ACCUSED]
[ADDRESS IF KNOWN]

From,
{name}
[ADDRESS]

Date: {today}
Notice Reference: LN/CYBER/{today.replace('/', '')}

SUBJECT: Legal Notice for Cessation of Online Harassment and Cyber Crime

Dear Sir/Madam,

This Legal Notice is being sent to you on behalf of {name} (hereinafter referred to as "my client") regarding the illegal, defamatory, and harassing conduct perpetrated by you against my client through electronic means.

ACTS COMPLAINED OF:
[DESCRIBE SPECIFIC HARASSING ACTS]

LEGAL VIOLATIONS:
Your aforesaid actions constitute criminal offences under {sections} of the IT Act 2000 and the Indian Penal Code, punishable by imprisonment and/or fine.

DEMANDS:
1. IMMEDIATELY and permanently cease all forms of online harassment, threats, and defamatory content directed at my client.
2. DELETE all content posted about my client within 24 hours of receipt of this notice.
3. DESTROY any intimate images, screenshots, or personal data of my client in your possession.
4. PROVIDE written undertaking that you will not repeat such conduct.

CONSEQUENCES OF NON-COMPLIANCE:
Failure to comply with the above demands within 7 days will leave my client with no alternative but to initiate criminal proceedings before the competent courts and file a complaint with the Cyber Crime Cell, in addition to civil proceedings claiming damages.

This notice is without prejudice to my client's other legal rights and remedies.

Issued by,
[ADVOCATE NAME / {name}]
Date: {today}"""
