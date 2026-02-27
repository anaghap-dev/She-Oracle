"""
Tool: threat_analyzer
Analyzes digital harassment evidence using NLP threat classification,
severity scoring, escalation prediction, and IT Act legal mapping.
"""
import json
from gemini_client import generate
from rag.embedder import embed_query
from rag.chroma_store import query_collection


# Harassment category taxonomy
THREAT_CATEGORIES = [
    "cyberstalking",
    "online_harassment",
    "sextortion",
    "ncii",              # Non-consensual intimate images
    "doxxing",
    "impersonation",
    "financial_fraud",
    "criminal_threats",
    "defamation",
    "cyberbullying",
]


def analyze_threat(evidence_text: str, context: str = "") -> dict:
    """
    Analyze digital harassment evidence for threat classification,
    severity scoring, legal mapping, and recommended escalation path.

    Args:
        evidence_text: The raw text content (screenshot OCR, message text, post content)
        context: Optional background context (platform, relationship to harasser, history)

    Returns:
        dict with: threat_type, severity_score, escalation_level, legal_sections,
                   immediate_actions, platform_actions, evidence_checklist, risk_factors
    """
    # RAG retrieval — pull relevant cyber law context
    q_emb = embed_query(f"cyber harassment law India {evidence_text[:200]}")
    results = query_collection(q_emb, n_results=6, where={"category": "cyber_laws"})

    law_chunks = []
    docs = results.get("documents", [[]])
    if docs and docs[0]:
        law_chunks = docs[0]

    law_context = "\n\n---\n\n".join(law_chunks)

    prompt = f"""You are SHE-ORACLE's Digital Protection Intelligence Engine — an expert in Indian cyber law, online harassment, and digital safety for women.

EVIDENCE TO ANALYZE:
{evidence_text}

ADDITIONAL CONTEXT (if any):
{context if context else "None provided"}

RELEVANT LEGAL KNOWLEDGE BASE:
{law_context if law_context else "Use your knowledge of Indian IT Act and IPC provisions."}

Perform a comprehensive threat intelligence analysis. Return ONLY valid JSON in this exact format:

{{
  "threat_classification": {{
    "primary_type": "one of: cyberstalking|online_harassment|sextortion|ncii|doxxing|impersonation|financial_fraud|criminal_threats|defamation|cyberbullying",
    "secondary_types": ["additional threat types present, if any"],
    "confidence": 0.95,
    "description": "2-sentence description of what this threat involves"
  }},
  "severity": {{
    "score": 7,
    "level": "one of: LOW|MODERATE|HIGH|CRITICAL",
    "justification": "Why this severity score was assigned — 2-3 sentences"
  }},
  "escalation_prediction": {{
    "likelihood_to_escalate": "HIGH",
    "risk_factors": ["List of specific risk factors present in the evidence"],
    "timeline": "Expected escalation timeline if no action taken"
  }},
  "legal_mapping": {{
    "primary_sections": [
      {{
        "act": "IT Act 2000 / IPC / BNS",
        "section": "Section 66E",
        "description": "Violation of Privacy",
        "punishment": "Imprisonment up to 3 years or fine up to Rs 2 lakh",
        "applicability": "Why this section applies to this case"
      }}
    ],
    "cognizable_offence": true,
    "bailable": false,
    "jurisdiction": "Where to file — Cyber Cell / Local Police / Both"
  }},
  "immediate_actions": [
    "Action 1 — most urgent first",
    "Action 2",
    "Action 3"
  ],
  "platform_actions": [
    {{
      "platform": "Platform name",
      "action": "Specific report/block steps",
      "reference_law": "IT Act section to cite in report"
    }}
  ],
  "evidence_checklist": [
    {{
      "item": "Screenshot with timestamp",
      "collected": false,
      "priority": "HIGH"
    }}
  ],
  "support_resources": [
    {{
      "name": "Resource name",
      "contact": "Phone/URL",
      "purpose": "What help they provide"
    }}
  ],
  "safety_warning": "Any immediate physical safety concern to flag — null if none"
}}"""

    text = generate(prompt)

    # Strip markdown fences
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        # Graceful fallback
        return {
            "threat_classification": {
                "primary_type": "online_harassment",
                "secondary_types": [],
                "confidence": 0.5,
                "description": "Unable to fully classify. Evidence requires manual review.",
            },
            "severity": {
                "score": 5,
                "level": "MODERATE",
                "justification": "Default moderate severity assigned due to analysis error. Please review manually.",
            },
            "escalation_prediction": {
                "likelihood_to_escalate": "UNKNOWN",
                "risk_factors": ["Manual review required"],
                "timeline": "Unknown",
            },
            "legal_mapping": {
                "primary_sections": [
                    {
                        "act": "IT Act 2000",
                        "section": "Section 66",
                        "description": "Computer Related Offences",
                        "punishment": "Imprisonment up to 3 years or fine up to Rs 5 lakh",
                        "applicability": "General cyber offence provision",
                    }
                ],
                "cognizable_offence": True,
                "bailable": True,
                "jurisdiction": "Local Cyber Cell",
            },
            "immediate_actions": [
                "Document all evidence with screenshots and timestamps",
                "File complaint at www.cybercrime.gov.in",
                "Contact Women Helpline: 1091",
            ],
            "platform_actions": [],
            "evidence_checklist": [
                {"item": "Screenshot with timestamp", "collected": False, "priority": "HIGH"},
                {"item": "Sender profile URL", "collected": False, "priority": "HIGH"},
                {"item": "All message history", "collected": False, "priority": "MEDIUM"},
            ],
            "support_resources": [
                {"name": "Cybercrime Portal", "contact": "www.cybercrime.gov.in", "purpose": "File online complaint"},
                {"name": "Women Helpline", "contact": "1091", "purpose": "Immediate support"},
                {"name": "Cyber Fraud Helpline", "contact": "1930", "purpose": "Financial fraud cases"},
            ],
            "safety_warning": None,
            "_raw_response": text,
        }
