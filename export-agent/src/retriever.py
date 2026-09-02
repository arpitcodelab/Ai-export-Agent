"""
retriever.py — Pipeline B (Step 1): Semantic Retrieval from ChromaDB
======================================================================
Given a user's question, finds the top-K most relevant knowledge base chunks.

This is the "librarian" — it doesn't generate any text, it just finds relevant facts.
The agent.py then uses these facts to build the LLM prompt.

Usage (standalone test):
  python src/retriever.py "What is IEC?"
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure stdout handles UTF-8 on Windows (knowledge base uses ₹, →, etc.)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = ROOT / "data" / "vector_store"
COLLECTION_NAME = "export_knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── Retrieval Settings ────────────────────────────────────────────────────────
# Minimum similarity score — below this, we consider "no relevant answer found"
# ChromaDB uses cosine distance (0 = identical, 2 = opposite)
# Distance threshold: 1.2 means cosine similarity ~0.4 (moderate match)
MAX_DISTANCE_THRESHOLD = 1.2

# Default top-K results to retrieve
DEFAULT_TOP_K = 5


# ─────────────────────────────────────────────────────────────────────────────
# Retriever class
# ─────────────────────────────────────────────────────────────────────────────

class Retriever:
    """
    Manages the ChromaDB connection and performs semantic search.
    Designed to be instantiated once (at app startup) and reused.
    """
    
    def __init__(self, top_k: int = DEFAULT_TOP_K):
        """Initialise the retriever, loading the ChromaDB index."""
        self.top_k = top_k
        self.collection = None
        self._load_collection()
    
    def _load_collection(self):
        """Load the ChromaDB collection. Raises RuntimeError if index not built."""
        try:
            import chromadb
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        except ImportError:
            raise RuntimeError(
                "chromadb not installed. Run: pip install chromadb sentence-transformers"
            )
        
        if not VECTOR_STORE_DIR.exists():
            raise RuntimeError(
                f"Vector store not found at {VECTOR_STORE_DIR}. "
                "Run: python src/build_index.py"
            )
        
        embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
        
        try:
            self.collection = client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=embed_fn
            )
        except Exception:
            raise RuntimeError(
                f"Collection '{COLLECTION_NAME}' not found. "
                "Run: python src/build_index.py"
            )
        
        count = self.collection.count()
        print(f"  [Retriever] Loaded ChromaDB index: {count} chunks available")
    
    def retrieve(self, question: str, top_k: Optional[int] = None) -> list[dict]:
        """
        Retrieve the top-K most relevant knowledge base chunks for a question.
        
        Args:
            question: The user's question text
            top_k: Override the default number of results
        
        Returns:
            List of chunk dicts. Empty list if no relevant results found.
            Each dict includes: id, topic, category, answer, source_name, 
                               source_url, distance (similarity score)
        """
        k = top_k or self.top_k
        k = min(k, self.collection.count())  # can't request more than we have
        
        if k == 0:
            return []
        
        results = self.collection.query(
            query_texts=[question],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        chunks = []
        ids = results["ids"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        for chunk_id, meta, distance in zip(ids, metadatas, distances):
            # Filter out chunks that are too far (not relevant enough)
            if distance > MAX_DISTANCE_THRESHOLD:
                continue
            
            chunk = {
                "id": chunk_id,
                "topic": meta.get("topic", ""),
                "category": meta.get("category", ""),
                "question_it_answers": meta.get("question_it_answers", ""),
                "answer": meta.get("answer", ""),
                "source_name": meta.get("source_name", ""),
                "source_url": meta.get("source_url", ""),
                "source_type": meta.get("source_type", ""),
                "last_verified_date": meta.get("last_verified_date", ""),
                "notes": meta.get("notes", ""),
                "_distance": round(distance, 4),  # for debugging
            }
            chunks.append(chunk)
        
        return chunks
    
    def get_categories_from_chunks(self, chunks: list[dict]) -> list[str]:
        """Extract unique categories from retrieved chunks (for prompt add-ons)."""
        return list(set(c.get("category", "") for c in chunks if c.get("category")))
    
    def health_check(self) -> dict:
        """Return info about the current index state."""
        if self.collection is None:
            return {"status": "error", "message": "No collection loaded"}
        
        count = self.collection.count()
        return {
            "status": "ok",
            "chunks_indexed": count,
            "collection": COLLECTION_NAME,
            "vector_store": str(VECTOR_STORE_DIR),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Singleton — shared across the app
# ─────────────────────────────────────────────────────────────────────────────

_retriever_instance: Optional[Retriever] = None


def get_retriever(top_k: int = DEFAULT_TOP_K) -> Retriever:
    """
    Get (or create) the singleton Retriever instance.
    Keeps the ChromaDB connection open across multiple queries.
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever(top_k=top_k)
    return _retriever_instance


def retrieve(question: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Convenience function: retrieve relevant chunks for a question.
    Automatically initialises the retriever on first call.
    """
    r = get_retriever(top_k)
    return r.retrieve(question, top_k)


# ─────────────────────────────────────────────────────────────────────────────
# CLI (for testing)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        question = "What is an IEC and how do I get one?"
    else:
        question = " ".join(sys.argv[1:])
    
    print(f"\nRetrieving chunks for: '{question}'")
    print("-" * 50)
    
    chunks = retrieve(question)
    
    if not chunks:
        print("No relevant chunks found (all distances above threshold).")
        print("This would trigger the 'I don't know' fallback in the agent.")
    else:
        print(f"Found {len(chunks)} relevant chunk(s):\n")
        for i, c in enumerate(chunks, 1):
            print(f"{i}. [{c['id']}] {c['topic']}")
            print(f"   Category: {c['category']}")
            print(f"   Source: {c['source_name']}")
            print(f"   Distance: {c['_distance']} (lower = more relevant)")
            print(f"   Answer snippet: {c['answer'][:200]}...")
            print()
