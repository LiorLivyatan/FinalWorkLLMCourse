# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""RAG knowledge base over the MCP Architecture book (English chapters).

Uses Agno's Knowledge + ChromaDB (local, persistent) + GeminiEmbedder.
Chapters are indexed once on first run; subsequent runs reuse the index.

Environment variables:
    CHROMA_PATH          - ChromaDB storage path (default: tmp/chromadb)
    COURSE_MATERIAL_PATH - Path to chapters_en directory (default: ../chapters_en)
    GOOGLE_API_KEY       - Required by GeminiEmbedder
"""
import os
from pathlib import Path
from typing import Optional

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_knowledge: Optional[Knowledge] = None


def _build_knowledge() -> Knowledge:
    chroma_path = os.getenv("CHROMA_PATH", "tmp/chromadb")
    return Knowledge(
        vector_db=ChromaDb(
            collection="mcp_book",
            path=chroma_path,
            persistent_client=True,
            embedder=GeminiEmbedder(
                id="gemini-embedding-2-preview",
                vertexai=True,
            ),
        ),
    )


def get_knowledge() -> Knowledge:
    global _knowledge
    if _knowledge is None:
        _knowledge = _build_knowledge()
    return _knowledge


def ensure_indexed() -> None:
    """Index MCP book chapters into ChromaDB if not already done."""
    course_path = os.getenv("COURSE_MATERIAL_PATH", "../chapters_en")
    material_dir = Path(course_path)
    if not material_dir.exists():
        return  # Skip silently if path not configured

    chroma_path = os.getenv("CHROMA_PATH", "tmp/chromadb")
    flag_file = Path(chroma_path) / ".indexed"
    if flag_file.exists():
        return

    kb = get_knowledge()
    kb.insert(path=str(material_dir))
    flag_file.parent.mkdir(parents=True, exist_ok=True)
    flag_file.touch()


def search(query: str, n_results: int = 3) -> list[dict]:
    """Search the MCP book knowledge base. Returns [] on any error."""
    try:
        kb = get_knowledge()
        documents = kb.search(query, max_results=n_results)
        return [{"content": doc.content} for doc in documents]
    except Exception:
        return []
