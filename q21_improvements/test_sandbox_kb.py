# Area: Data Engineering — Sandbox Knowledge Base Test
"""
Compare RAG search quality: broken (Agno/pypdf) vs fixed (PyMuPDF) indexing.

Extracts text from course PDFs using PyMuPDF (correct RTL Hebrew),
indexes into a sandbox ChromaDB collection, then runs identical
queries against both collections to compare result quality.

Usage:  python q21_improvements/test_sandbox_kb.py
"""
import os
import sys
import fitz  # PyMuPDF
import chromadb
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl")
)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

CHROMA_PATH = os.getenv("CHROMA_PATH", "./database")
COURSE_PATH = os.getenv("COURSE_MATERIAL_PATH", "./course-material")
SANDBOX_COLLECTION = "course_material_fixed"
BROKEN_COLLECTION = "course_material"

# ── ANSI ────────────────────────────────────────────────────────
R = "\033[0m"; B = "\033[1m"; G = "\033[92m"; RED = "\033[91m"
CY = "\033[36m"; DIM = "\033[2m"; YEL = "\033[33m"


def extract_pdf_pymupdf(pdf_path: str) -> list[dict]:
    """Extract pages from a PDF using PyMuPDF (correct RTL)."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({
                "content": text,
                "name": os.path.basename(pdf_path),
                "page": i + 1,
            })
    doc.close()
    return pages


def build_sandbox_collection():
    """Index course PDFs into a sandbox collection using PyMuPDF."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing sandbox if present
    try:
        client.delete_collection(SANDBOX_COLLECTION)
    except Exception:
        pass

    col = client.get_or_create_collection(
        name=SANDBOX_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    pdf_dir = Path(COURSE_PATH)
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    print(f"{CY}{B}Indexing {len(pdfs)} PDFs with PyMuPDF...{R}")

    all_docs = []
    all_ids = []
    all_metas = []

    for pdf in pdfs:
        pages = extract_pdf_pymupdf(str(pdf))
        for p in pages:
            doc_id = f"{p['name']}_p{p['page']}"
            all_docs.append(p["content"])
            all_ids.append(doc_id)
            all_metas.append({"name": p["name"], "page": p["page"]})

    # Batch insert (ChromaDB default embedder)
    BATCH = 100
    for i in range(0, len(all_docs), BATCH):
        col.add(
            documents=all_docs[i:i+BATCH],
            ids=all_ids[i:i+BATCH],
            metadatas=all_metas[i:i+BATCH],
        )
    print(f"  Indexed {col.count()} documents into '{SANDBOX_COLLECTION}'")
    return col


def compare_search(query: str, label: str):
    """Run query against FIXED collection; show BROKEN content for same PDF."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    print(f"\n{YEL}{B}Query: {query}{R}")
    print(f"{DIM}  Label: {label}{R}")

    # Query the fixed collection (default embedder, 384-dim)
    fixed = client.get_collection(SANDBOX_COLLECTION)
    results = fixed.query(query_texts=[query], n_results=3)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    # Get the broken collection for content comparison (no query — get by ID)
    broken = client.get_collection(BROKEN_COLLECTION)

    print(f"  [{G}FIXED{R}]")
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
        src = f"{meta.get('name','?')}:p{meta.get('page','?')}"
        print(f"    [{i}] dist={dist:.4f} src={src}")
        print(f"        {DIM}{doc[:120]}{R}")

    # Show what the BROKEN collection has for the same source file
    if metas:
        top_name = metas[0].get("name", "")
        top_page = metas[0].get("page", 1)
        broken_docs = broken.get(
            where={"name": top_name}, limit=1, include=["documents"]
        )
        if broken_docs["documents"]:
            print(f"  [{RED}BROKEN{R}] same file ({top_name}):")
            print(f"        {DIM}{broken_docs['documents'][0][:120]}{R}")


def main():
    print(f"\n{B}  Sandbox KB Test: Broken (pypdf) vs Fixed (PyMuPDF){R}\n")

    # Step 1: Build sandbox
    sandbox_col = build_sandbox_collection()

    # Step 2: Compare searches
    test_queries = [
        ("הגבלת 150 שורות לקובץ", "150-line file limit (scenario 1)"),
        ("ארכיטקטורת תוכנה סוכנים", "Software architecture for agents"),
        ("Gmail API transport layer", "Gmail transport (scenario 3)"),
        ("שכבת תעבורה Gmail", "Gmail transport Hebrew"),
        ("עקרונות עיצוב מערכת", "Design principles (scenario 2)"),
        ("150 line limit per file is not arbitrary", "Scenario 1 English"),
    ]

    for query, label in test_queries:
        compare_search(query, label)

    print()


if __name__ == "__main__":
    main()
