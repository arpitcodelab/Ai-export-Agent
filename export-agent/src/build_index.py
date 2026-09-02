"""
build_index.py — Pipeline A (Step 2): Build ChromaDB Search Index
==================================================================
Reads knowledge_base.json and builds a semantic search index in ChromaDB.
Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings — free, runs locally.

Run AFTER ingest.py:
  python src/build_index.py

This is safe to re-run — it clears and rebuilds the index from scratch each time.
Rebuilding takes ~1-3 minutes depending on your hardware.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
KB_JSON = ROOT / "data" / "processed" / "knowledge_base.json"
VECTOR_STORE_DIR = ROOT / "data" / "vector_store"
COLLECTION_NAME = "export_knowledge_base"

# ── Embedding model ───────────────────────────────────────────────────────────
# all-MiniLM-L6-v2: fast, free, 384-dimensional, good for Q&A retrieval
# Downloaded once to ~/.cache/huggingface/hub/ — no API cost ever
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_knowledge_base() -> list[dict]:
    """Load chunks from knowledge_base.json."""
    if not KB_JSON.exists():
        print(f"ERROR: {KB_JSON} not found.")
        print("       Run  python src/ingest.py  first to create it.")
        sys.exit(1)
    
    with open(KB_JSON, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"  Loaded {len(chunks)} chunks from {KB_JSON.name}")
    return chunks


def filter_review_chunks(chunks: list[dict]) -> tuple[list[dict], int]:
    """
    Filter out chunks marked 'REVIEW NEEDED' — they shouldn't be in the live index.
    Returns (filtered_chunks, skipped_count).
    """
    clean = [c for c in chunks if "[REVIEW NEEDED]" not in str(c.get("answer", ""))]
    skipped = len(chunks) - len(clean)
    if skipped > 0:
        print(f"  ⚠️  Skipped {skipped} chunks marked 'REVIEW NEEDED' (not indexed)")
    return clean, skipped


def prepare_documents(chunks: list[dict]) -> tuple[list[str], list[str], list[dict]]:
    """
    Prepare the text, IDs, and metadata for ChromaDB ingestion.
    
    The text indexed for each chunk combines the topic, question, and answer
    so semantic search can match against any of these.
    
    Returns:
        documents: list of text strings to embed
        ids: list of unique IDs
        metadatas: list of metadata dicts (stored alongside the vector)
    """
    documents = []
    ids = []
    metadatas = []
    
    for chunk in chunks:
        # Build the text that gets embedded (what semantic search runs against)
        text = f"""Topic: {chunk.get('topic', '')}
Question: {chunk.get('question_it_answers', '')}
Answer: {chunk.get('answer', '')}"""
        
        # Metadata stored in ChromaDB (returned alongside search results)
        metadata = {
            "id": chunk.get("id", ""),
            "topic": chunk.get("topic", ""),
            "category": chunk.get("category", ""),
            "question_it_answers": chunk.get("question_it_answers", ""),
            "answer": chunk.get("answer", "")[:2000],  # Truncate for metadata storage
            "source_name": chunk.get("source_name", ""),
            "source_url": chunk.get("source_url", ""),
            "source_type": chunk.get("source_type", ""),
            "last_verified_date": chunk.get("last_verified_date", ""),
            "notes": chunk.get("notes", ""),
        }
        
        documents.append(text)
        ids.append(chunk.get("id", f"chunk-{len(ids)}"))
        metadatas.append(metadata)
    
    return documents, ids, metadatas


def build_index():
    """Main function: load KB → embed → store in ChromaDB."""
    
    print("\n" + "="*60)
    print("PIPELINE A (Step 2): Building ChromaDB Search Index")
    print("="*60)
    
    # ── Import ChromaDB ──────────────────────────────────────────────────────
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError:
        print("ERROR: chromadb not installed. Run: pip install chromadb")
        sys.exit(1)
    
    # ── Import sentence-transformers ─────────────────────────────────────────
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        print(f"\n[1/4] Embedding model: {EMBEDDING_MODEL}")
        print("      (Will download ~90MB on first run — subsequent runs use cache)")
    except Exception as e:
        print(f"ERROR loading embedding model: {e}")
        print("      Run: pip install sentence-transformers")
        sys.exit(1)
    
    # ── Load knowledge base ──────────────────────────────────────────────────
    print("\n[2/4] Loading knowledge base...")
    chunks = load_knowledge_base()
    chunks, skipped = filter_review_chunks(chunks)
    
    if not chunks:
        print("ERROR: No valid chunks to index. Check your knowledge_base.json.")
        sys.exit(1)
    
    # ── Prepare documents ────────────────────────────────────────────────────
    documents, ids, metadatas = prepare_documents(chunks)
    print(f"  Prepared {len(documents)} documents for indexing")
    
    # ── Set up ChromaDB ──────────────────────────────────────────────────────
    print(f"\n[3/4] Setting up ChromaDB at {VECTOR_STORE_DIR}...")
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    
    # Delete and recreate collection (clean rebuild each time)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"  Deleted existing collection '{COLLECTION_NAME}' (fresh rebuild)")
    except Exception:
        pass  # Collection didn't exist yet
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"description": "AI Export Facilitation Agent — Knowledge Base"}
    )
    
    # ── Index in batches ─────────────────────────────────────────────────────
    print(f"\n[4/4] Indexing {len(documents)} chunks...")
    
    BATCH_SIZE = 50  # ChromaDB handles this well
    total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(documents))
        
        collection.add(
            documents=documents[start:end],
            ids=ids[start:end],
            metadatas=metadatas[start:end],
        )
        print(f"  Batch {batch_num+1}/{total_batches}: indexed chunks {start+1}–{end}")
    
    # ── Verify ───────────────────────────────────────────────────────────────
    count = collection.count()
    
    print("\n" + "="*60)
    print(f"[OK] Index built successfully!")
    print(f"   {count} chunks indexed in ChromaDB")
    print(f"   Vector store location: {VECTOR_STORE_DIR}")
    print(f"\n   Quick test — searching for 'IEC registration':")
    test_results = collection.query(
        query_texts=["How do I get an IEC?"],
        n_results=min(3, count)
    )
    for i, (doc_id, meta) in enumerate(zip(
        test_results["ids"][0],
        test_results["metadatas"][0]
    )):
        print(f"   {i+1}. [{doc_id}] {meta.get('topic', '')}")
    
    print(f"\n   Next step: run  streamlit run app.py")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_index()
