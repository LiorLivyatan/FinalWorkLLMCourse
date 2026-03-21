# Area: Player AI - Knowledge Base Re-indexer
# PRD: docs/prd-player-ai.md
"""Re-index course PDFs with PyMuPDF (correct RTL) + GeminiEmbedder.

Replaces the broken Agno/pypdf-indexed collection with correctly
extracted Hebrew text. Uses the same GeminiEmbedder (1536-dim)
and ChromaDB collection name so knowledge_base.py works unchanged.

Usage:
    python Q21G-player-whl/reindex_kb.py [--dry-run]

This will:
1. Extract all PDFs with PyMuPDF (correct RTL Hebrew)
2. Chunk into ~2000 char paragraphs
3. Embed with GeminiEmbedder (gemini-embedding-2-preview)
4. Replace the 'course_material' collection in ChromaDB
"""
import os
import sys
import time
import hashlib

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

import chromadb
from agno.knowledge.embedder.google import GeminiEmbedder

from pdf_reader_fixed import extract_and_chunk_pdfs

CHROMA_PATH = os.getenv("CHROMA_PATH", "./database")
COURSE_PATH = os.getenv("COURSE_MATERIAL_PATH", "./course-material")
COLLECTION = "course_material"
BATCH_SIZE = 20  # small batches to avoid rate limits
SLEEP_BETWEEN = 2  # seconds between batches


def make_id(name: str, page: int, chunk: int) -> str:
    """Deterministic document ID."""
    raw = f"{name}:p{page}:c{chunk}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def embed_batch(embedder, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts, with retry on rate limit."""
    embeddings = []
    for text in texts:
        for attempt in range(3):
            try:
                emb = embedder.get_embedding(text)
                embeddings.append(emb)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = 30 * (attempt + 1)
                    print(f"  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise
    return embeddings


def main():
    dry_run = "--dry-run" in sys.argv

    print(f"Course PDFs: {COURSE_PATH}")
    print(f"ChromaDB:    {CHROMA_PATH}")
    print(f"Collection:  {COLLECTION}")
    print(f"Dry run:     {dry_run}\n")

    # Step 1: Extract and chunk
    print("Extracting PDFs with PyMuPDF...")
    chunks = extract_and_chunk_pdfs(COURSE_PATH, chunk_size=2000)
    print(f"  {len(chunks)} chunks from course material\n")

    if dry_run:
        for c in chunks[:5]:
            print(f"  [{c['name']}:p{c['page']}:c{c['chunk']}] "
                  f"({len(c['content'])} chars)")
            print(f"    {c['content'][:100]}...")
        print(f"\n  ... and {len(chunks)-5} more. Use without "
              f"--dry-run to index.")
        return

    # Step 2: Set up embedder and collection
    embedder = GeminiEmbedder(
        id="gemini-embedding-2-preview", vertexai=False,
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Delete old broken collection
    try:
        client.delete_collection(COLLECTION)
        print(f"Deleted old '{COLLECTION}' collection")
    except Exception:
        pass

    col = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    # Step 3: Embed and insert in batches
    total = len(chunks)
    print(f"Embedding and indexing {total} chunks "
          f"(batch={BATCH_SIZE}, sleep={SLEEP_BETWEEN}s)...\n")

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        ids = [make_id(c["name"], c["page"], c["chunk"]) for c in batch]
        metas = [{"name": c["name"], "page": c["page"],
                  "chunk": c["chunk"]} for c in batch]

        embeddings = embed_batch(embedder, texts)

        col.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metas,
        )

        done = min(i + BATCH_SIZE, total)
        print(f"  [{done}/{total}] indexed", end="")
        if done < total:
            print(f" — sleeping {SLEEP_BETWEEN}s...", end="")
            time.sleep(SLEEP_BETWEEN)
        print()

    # Step 4: Update flag file
    flag = os.path.join(CHROMA_PATH, ".indexed")
    with open(flag, "w") as f:
        f.write("reindexed with PyMuPDF + GeminiEmbedder\n")

    print(f"\nDone! {col.count()} documents in '{COLLECTION}'")


if __name__ == "__main__":
    main()
