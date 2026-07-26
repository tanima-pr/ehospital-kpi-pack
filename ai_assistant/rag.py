"""
rag.py — the retrieval engine. Two jobs:
  1. embed(text)  -> turn text into a list of numbers (a "vector") that captures
                     its meaning. Similar meanings -> similar vectors.
  2. retrieve(q)  -> find the knowledge chunks whose vectors are most similar to
                     the question's vector. Those are the relevant facts to show the AI.

This is the whole idea of RAG in ~40 lines. Real tools (Vanna, LangChain) do
exactly this with more polish.
"""
import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from knowledge_base import KNOWLEDGE

load_dotenv()

EMBED_MODEL = "gemini-embedding-001"   # free Gemini embedding model
_client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


def embed(texts):
    """Turn a list of strings into a list of vectors (numbers)."""
    resp = _client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [np.array(d.embedding, dtype=np.float32) for d in resp.data]


def _cosine(a, b):
    """How similar are two vectors? 1.0 = identical meaning, 0 = unrelated."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


# Embed the whole knowledge base ONCE when this module loads (small, so it's fast).
print(f"Embedding {len(KNOWLEDGE)} knowledge chunks... (one-time, a few seconds)")
_KB_VECTORS = embed([k["text"] for k in KNOWLEDGE])
print("Knowledge base ready.\n")


def retrieve(question, k=4):
    """Return the k most relevant knowledge chunks for this question."""
    qv = embed([question])[0]
    scored = [(_cosine(qv, vec), kb) for vec, kb in zip(_KB_VECTORS, KNOWLEDGE)]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]   # list of (similarity_score, chunk)


if __name__ == "__main__":
    # Quick demo: what does it pull up for a margin question?
    for score, chunk in retrieve("weekly cancellation rate"):
        print(f"[{score:.2f}] ({chunk['type']}) {chunk['text'][:70]}...")
