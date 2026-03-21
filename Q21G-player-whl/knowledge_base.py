# Area: Player AI - Knowledge Base
# PRD: docs/prd-player-ai.md
"""RAG knowledge base over course material PDFs.

Uses Agno's Knowledge + ChromaDB (local, persistent) + GeminiEmbedder.
PDFs are indexed once on first run; subsequent runs reuse the index.

Environment variables:
    CHROMA_PATH          - ChromaDB storage path (default: database)
    COURSE_MATERIAL_PATH - Directory containing the 22 course PDFs
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
    """Create a new Knowledge instance backed by ChromaDB + Gemini."""
    chroma_path = os.getenv("CHROMA_PATH", "../database")
    return Knowledge(
        vector_db=ChromaDb(
            collection="course_material",
            path=chroma_path,
            persistent_client=True,
            embedder=GeminiEmbedder(
                id="gemini-embedding-2-preview",
                vertexai=False,
            ),
        ),
    )


def get_knowledge() -> Knowledge:
    """Return the singleton Knowledge instance."""
    global _knowledge
    if _knowledge is None:
        _knowledge = _build_knowledge()
    return _knowledge


def ensure_indexed() -> None:
    """Index course material PDFs into ChromaDB if not already done.

    Uses a flag file (.indexed) inside the ChromaDB directory to
    avoid re-indexing on every startup.

    Raises:
        FileNotFoundError: If COURSE_MATERIAL_PATH doesn't exist.
    """
    course_path = os.getenv("COURSE_MATERIAL_PATH", "../course-material")
    material_dir = Path(course_path)

    if not material_dir.exists():
        raise FileNotFoundError(
            f"Course material not found at: {material_dir.resolve()}"
        )

    chroma_path = os.getenv("CHROMA_PATH", "../database")
    flag_file = Path(chroma_path) / ".indexed"

    if flag_file.exists():
        return

    kb = get_knowledge()
    kb.insert(path=str(material_dir))

    flag_file.parent.mkdir(parents=True, exist_ok=True)
    flag_file.touch()


def search(query: str, n_results: int = 5) -> list[dict]:
    """Search the knowledge base for relevant content.

    Args:
        query: Natural language search query.
        n_results: Maximum number of results to return.

    Returns:
        List of dicts with 'content' key containing matched text.
    """
    kb = get_knowledge()
    documents = kb.search(query, max_results=n_results)
    return [{"content": doc.content} for doc in documents]
