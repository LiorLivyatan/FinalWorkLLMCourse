# Area: Player AI - Integration
# PRD: docs/prd-player-ai.md
"""Integration tests requiring real API keys and services.

Run with: pytest tests/integration/ -m integration
"""
import os
import pytest

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _require_api_key():
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")


class TestGeminiConnection:
    def test_simple_math(self):
        from gemini_client import generate

        result = generate(
            "What is 2 + 2? Answer with ONLY the number, nothing else."
        )
        assert "4" in result.strip()

    def test_generate_json(self):
        from gemini_client import generate_json

        result = generate_json(
            'Return a JSON object with a single key "color" and value "blue".'
        )
        assert isinstance(result, dict)
        assert result.get("color") == "blue"


class TestKnowledgeBase:
    def test_search_existing_index(self):
        """Search the pre-built index (must run indexing first)."""
        chroma_path = os.getenv("CHROMA_PATH", "../database")
        flag = os.path.join(chroma_path, ".indexed")
        if not os.path.exists(flag):
            pytest.skip("Index not built yet — run ensure_indexed() first")

        from knowledge_base import search

        results = search("neural networks deep learning", n_results=3)
        assert len(results) > 0
        assert "content" in results[0]


class TestPlayerEndToEnd:
    def test_warmup_solves_math(self):
        from gemini_client import generate

        answer = generate("What is 12 * 7? Reply with ONLY the number.")
        assert "84" in answer.strip()
