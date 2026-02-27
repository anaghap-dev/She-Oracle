"""
Tool: legal_rights_checker
Analyzes a workplace/legal situation against Indian labor laws and
generates grounded legal intelligence with escalation strategies.
"""
import json
from gemini_client import generate
from rag.embedder import embed_query
from rag.chroma_store import query_collection


def legal_rights_checker(situation: str, situation_type: str = "workplace") -> dict:
    """
    Check legal rights and remedies for a given situation.

    Args:
        situation: Description of the legal/workplace situation
        situation_type: One of 'workplace', 'harassment', 'domestic', 'wage', 'maternity'

    Returns:
        dict with rights violated, remedies, escalation steps, document drafts
    """
    q_emb = embed_query(situation)
    results = query_collection(q_emb, n_results=6, where={"category": "legal"})

    context_chunks = results.get("documents", [[]])[0] if results.get("documents") else []
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are SHE-ORACLE's Legal Protection Agent — an expert on Indian labor laws, women's rights, and workplace justice.

Situation Described: {situation}
Situation Type: {situation_type}

Relevant Legal Provisions:
{context}

Analyze this situation and provide a comprehensive legal intelligence report as JSON.

Return ONLY valid JSON in this exact format:
{{
  "rights_violated": [
    {{
      "law": "Law/Act name",
      "section": "Section number",
      "violation": "How this law is being violated",
      "penalty_for_employer": "What employer faces"
    }}
  ],
  "immediate_protections": [
    "Protection available right now"
  ],
  "escalation_strategy": [
    {{
      "step": 1,
      "action": "What to do",
      "authority": "Who to contact",
      "timeline": "Within X days",
      "expected_outcome": "What this achieves"
    }}
  ],
  "documentation_required": [
    "Document 1 to collect/preserve"
  ],
  "helplines": [
    {{
      "name": "Helpline name",
      "number": "Phone number",
      "for": "When to use this"
    }}
  ],
  "draft_complaint_opening": "Draft opening paragraph for a formal complaint letter",
  "risk_assessment": "Assessment of the situation's legal strength (strong/moderate/weak) with reasoning",
  "free_legal_aid": "How to access free legal aid for this situation"
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
            "rights_violated": [],
            "immediate_protections": [],
            "escalation_strategy": [],
            "documentation_required": [],
            "helplines": [{"name": "Women Helpline", "number": "181", "for": "Any emergency"}],
            "draft_complaint_opening": "",
            "risk_assessment": text,
            "free_legal_aid": "Contact National Legal Services Authority at 15100 for free legal aid.",
        }
