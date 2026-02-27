"""
RAG Retriever Agent — retrieves relevant knowledge chunks from ChromaDB.
"""
from rag.embedder import embed_query
from rag.chroma_store import query_collection


CATEGORY_MAP = {
    "legal": "legal",
    "career": None,
    "financial": None,
    "education": "education",
    "grants": "grants",
    "schemes": "schemes",
}


def retrieve(query: str, domain: str = None, n_results: int = 5) -> list[dict]:
    """
    Retrieve relevant knowledge chunks for a query.

    Args:
        query: Search query string
        domain: Optional domain filter ('legal', 'education', 'grants', 'schemes')
        n_results: Number of chunks to retrieve

    Returns:
        List of dicts with 'text', 'source', 'category', 'score'
    """
    q_emb = embed_query(query)

    category = CATEGORY_MAP.get(domain) if domain else None
    where_filter = {"category": category} if category else None

    results = query_collection(q_emb, n_results=n_results, where=where_filter)

    docs = results.get("documents", [[]])[0] or []
    metas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    chunks = []
    for doc, meta, dist in zip(docs, metas, distances):
        chunks.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "category": meta.get("category", "general"),
            "score": round(1 - dist, 4),  # cosine similarity
        })

    return chunks


def retrieve_formatted(query: str, domain: str = None, n_results: int = 5) -> str:
    """Returns retrieved chunks as a formatted string for LLM context."""
    chunks = retrieve(query, domain, n_results)
    if not chunks:
        return "No relevant knowledge found in the database."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Source {i}: {chunk['source']} | Score: {chunk['score']}]\n{chunk['text']}")

    return "\n\n---\n\n".join(parts)
