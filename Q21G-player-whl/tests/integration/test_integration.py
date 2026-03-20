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
    def test_ensure_indexed_runs(self, tmp_path, monkeypatch):
        """Test indexing with a tiny test PDF."""
        monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chromadb"))

        course_dir = os.getenv(
            "COURSE_MATERIAL_PATH", "../course-material"
        )
        if not os.path.isdir(course_dir):
            pytest.skip("Course material directory not found")

        import knowledge_base
        knowledge_base._knowledge = None  # reset singleton

        knowledge_base.ensure_indexed()
        results = knowledge_base.search("multi-agent systems", n_results=3)

        assert len(results) > 0
        assert "content" in results[0]

        knowledge_base._knowledge = None  # cleanup


class TestPlayerEndToEnd:
    def test_warmup_solves_math(self):
        """Full warmup flow with real Gemini."""
        # Import directly to avoid knowledge base init
        from gemini_client import generate

        answer = generate(
            "What is 12 * 7? Reply with ONLY the number."
        )
        assert "84" in answer.strip()
