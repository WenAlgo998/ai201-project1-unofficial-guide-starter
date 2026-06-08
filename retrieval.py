"""
Milestone 4 — Embedding + vector store + retrieval for the Unofficial Guide.

Implements the Retrieval Approach from planning.md:
  - Embedding model: all-MiniLM-L6-v2 (local, 384-dim) via sentence-transformers.
  - Vector store: ChromaDB, persisted to ./chroma_db, with cosine distance so the
    scores match the "below 0.5 = good match" intuition.
  - retrieve(query, k=6): embed the query, return the top-k chunks + metadata + distance.

Run directly to (re)build the index and test retrieval on the evaluation queries:
    python retrieval.py
"""

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import build_chunks

MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "professor_reviews"
DEFAULT_K = 6  # from planning.md Retrieval Approach

# Load the embedding model once at import time (it's reused for both indexing
# and querying so the same vector space is used on each side).
_model = SentenceTransformer(MODEL_NAME)
_client = chromadb.PersistentClient(path=CHROMA_PATH)


def _clean_metadata(metadata: dict) -> dict:
    """ChromaDB only accepts str/int/float/bool metadata values — drop any None
    (e.g., reviews with no course code or no quality score)."""
    return {k: v for k, v in metadata.items() if v is not None}


def embed_and_store() -> chromadb.Collection:
    """Build chunks, embed them with all-MiniLM-L6-v2, and (re)load them into a
    fresh ChromaDB collection with their metadata. Returns the collection."""
    chunks = build_chunks()

    # Start clean each run so re-running doesn't duplicate or stale-cache chunks.
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = _client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine distance, range ~0..2
    )

    texts = [c.text for c in chunks]
    embeddings = _model.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=[c.id for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[_clean_metadata(c.metadata) for c in chunks],
    )
    return collection


def _get_collection() -> chromadb.Collection:
    """Return the existing collection, building it if it hasn't been created yet."""
    try:
        return _client.get_collection(COLLECTION_NAME)
    except Exception:
        return embed_and_store()


def retrieve(query: str, k: int = DEFAULT_K) -> list[dict]:
    """Embed the query and return the top-k chunks as dicts with text, metadata,
    and cosine distance (lower = more relevant)."""
    collection = _get_collection()
    query_embedding = _model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    hits = []
    for text, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": text, "metadata": meta, "distance": dist})
    return hits


# --- Retrieval test on the evaluation queries -----------------------------

if __name__ == "__main__":
    print(f"Building index with {MODEL_NAME}...")
    collection = embed_and_store()
    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}'.\n")

    # 3+ of the 5 evaluation-plan queries from planning.md.
    test_queries = [
        "Which professor should I take for Data Structures (CSC 212)?",
        "What do students say about cheating in Jie Wei's CSC 322 class?",
        "Who is a good professor for an easy A with a light workload?",
        "How hard is Douglas Troeger's algorithms class CSC 335?",
    ]

    # Tuning note: started at k=4 (per milestone). For the "Data Structures
    # CSC 212" query, k=4 returned only CSC 103 intro reviews; bumping to k=6
    # (the planning.md value) recovers Prof. Wolberg's CSC 212 review at rank 5,
    # so k=6 is kept.
    for q in test_queries:
        print("=" * 78)
        print(f"QUERY: {q}")
        print("=" * 78)
        for i, hit in enumerate(retrieve(q, k=DEFAULT_K), 1):
            m = hit["metadata"]
            print(f"\n  {i}. distance={hit['distance']:.3f}  "
                  f"[{m.get('professor')} / {m.get('course', 'n/a')}]")
            print(f"     {hit['text']}")
        print()
