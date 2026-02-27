"""
Tool: grant_finder
Searches the knowledge base for relevant grants and government schemes,
then uses Gemini to synthesize a structured response.
"""
import json
from gemini_client import generate
from rag.embedder import embed_query
from rag.chroma_store import query_collection


def grant_finder(query: str, domain: str = "general") -> dict:
    """
    Find relevant grants, schemes, and funding programs.

    Args:
        query: User's goal or funding need description
        domain: One of 'startup', 'education', 'agriculture', 'general'

    Returns:
        dict with keys: grants (list), total_found (int), recommendation (str)
    """
    # RAG retrieval — filter by grants/schemes categories
    q_emb = embed_query(query)

    results_grants = query_collection(q_emb, n_results=4, where={"category": "grants"})
    results_schemes = query_collection(q_emb, n_results=3, where={"category": "schemes"})

    context_chunks = []
    for docs in [results_grants.get("documents", [[]]), results_schemes.get("documents", [[]])]:
        if docs and docs[0]:
            context_chunks.extend(docs[0])

    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are SHE-ORACLE's Grant Intelligence Agent — an expert on Indian government schemes and funding programs for women.

User Goal: {query}
Domain: {domain}

Relevant Knowledge Base Excerpts:
{context}

Based on the above, provide a structured JSON response identifying the TOP 5 most relevant grants/schemes for this user.

Return ONLY valid JSON in this exact format:
{{
  "grants": [
    {{
      "name": "Scheme/Grant Name",
      "type": "Grant/Loan/Subsidy/Recognition",
      "amount": "Amount or range",
      "eligibility": "Key eligibility criteria",
      "how_to_apply": "Application process",
      "portal": "URL or office",
      "timeline": "When to apply / processing time",
      "fit_score": 9
    }}
  ],
  "total_found": 5,
  "recommendation": "Top recommendation explanation in 2-3 sentences",
  "immediate_action": "What the user should do right now"
}}"""

    text = generate(prompt)

    # Clean markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "grants": [],
            "total_found": 0,
            "recommendation": text,
            "immediate_action": "Visit myscheme.gov.in for all government schemes.",
        }
