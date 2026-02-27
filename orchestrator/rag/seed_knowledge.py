"""
One-time script to seed the ChromaDB knowledge base.
Run: python rag/seed_knowledge.py
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from rag.embedder import embed_texts
from rag.chroma_store import add_documents, collection_count, get_collection

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge")

KNOWLEDGE_FILES = {
    "indian_labor_laws.txt": "legal",
    "government_schemes.txt": "schemes",
    "scholarships.txt": "education",
    "grants_programs.txt": "grants",
    "cyber_laws.txt": "cyber_laws",
}

CHUNK_SIZE = 500   # characters
CHUNK_OVERLAP = 80


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def seed():
    print("Starting knowledge base seeding...")
    total_chunks = 0

    for filename, category in KNOWLEDGE_FILES.items():
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename} not found.")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)
        print(f"  [{category.upper()}] {filename}: {len(chunks)} chunks")

        # Embed in batches of 32
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            embeddings = embed_texts(batch)
            ids = [str(uuid.uuid4()) for _ in batch]
            metadatas = [{"category": category, "source": filename, "chunk_index": i + j} for j, _ in enumerate(batch)]
            add_documents(ids=ids, embeddings=embeddings, documents=batch, metadatas=metadatas)

        total_chunks += len(chunks)

    print(f"\nSeeding complete. Total chunks in DB: {collection_count()}")


if __name__ == "__main__":
    seed()
