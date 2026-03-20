# Area: Player AI - Knowledge Base
# PRD: docs/prd-player-ai.md
"""Unit tests for knowledge_base module."""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestBuildKnowledge:
    def test_returns_knowledge_instance(self, mocker, monkeypatch):
        monkeypatch.setenv("CHROMA_PATH", "/tmp/test_chromadb")
        mock_chroma = mocker.patch("knowledge_base.ChromaDb")
        mock_embedder = mocker.patch("knowledge_base.GeminiEmbedder")

        from knowledge_base import _build_knowledge
        kb = _build_knowledge()

        from agno.knowledge.knowledge import Knowledge
        assert isinstance(kb, Knowledge)
        mock_chroma.assert_called_once()
        mock_embedder.assert_called_once()

    def test_uses_chroma_path_from_env(self, mocker, monkeypatch):
        monkeypatch.setenv("CHROMA_PATH", "/custom/chroma/path")
        mock_chroma = mocker.patch("knowledge_base.ChromaDb")
        mocker.patch("knowledge_base.GeminiEmbedder")

        from knowledge_base import _build_knowledge
        _build_knowledge()

        call_kwargs = mock_chroma.call_args[1]
        assert call_kwargs["path"] == "/custom/chroma/path"


class TestGetKnowledge:
    def test_returns_singleton(self, mocker, monkeypatch):
        mocker.patch("knowledge_base.ChromaDb")
        mocker.patch("knowledge_base.GeminiEmbedder")

        import knowledge_base
        knowledge_base._knowledge = None  # reset singleton

        kb1 = knowledge_base.get_knowledge()
        kb2 = knowledge_base.get_knowledge()
        assert kb1 is kb2

        knowledge_base._knowledge = None  # cleanup


class TestEnsureIndexed:
    def test_inserts_when_no_flag_file(self, mocker, monkeypatch, tmp_path):
        chroma_dir = tmp_path / "chromadb"
        chroma_dir.mkdir()
        monkeypatch.setenv("CHROMA_PATH", str(chroma_dir))

        course_dir = tmp_path / "course-material"
        course_dir.mkdir()
        (course_dir / "test.pdf").touch()
        monkeypatch.setenv("COURSE_MATERIAL_PATH", str(course_dir))

        mock_kb = MagicMock()
        mocker.patch("knowledge_base.get_knowledge", return_value=mock_kb)

        from knowledge_base import ensure_indexed
        ensure_indexed()

        mock_kb.insert.assert_called_once()
        assert (chroma_dir / ".indexed").exists()

    def test_skips_when_flag_exists(self, mocker, monkeypatch, tmp_path):
        chroma_dir = tmp_path / "chromadb"
        chroma_dir.mkdir()
        (chroma_dir / ".indexed").touch()
        monkeypatch.setenv("CHROMA_PATH", str(chroma_dir))
        monkeypatch.setenv("COURSE_MATERIAL_PATH", str(tmp_path))

        mock_kb = MagicMock()
        mocker.patch("knowledge_base.get_knowledge", return_value=mock_kb)

        from knowledge_base import ensure_indexed
        ensure_indexed()

        mock_kb.insert.assert_not_called()

    def test_raises_when_course_material_missing(self, mocker, monkeypatch, tmp_path):
        monkeypatch.setenv("CHROMA_PATH", str(tmp_path))
        monkeypatch.setenv("COURSE_MATERIAL_PATH", "/nonexistent/path")

        mock_kb = MagicMock()
        mocker.patch("knowledge_base.get_knowledge", return_value=mock_kb)

        from knowledge_base import ensure_indexed
        with pytest.raises(FileNotFoundError):
            ensure_indexed()


class TestSearch:
    def test_returns_list_of_dicts(self, mocker):
        from agno.knowledge.document import Document

        mock_kb = MagicMock()
        mock_kb.search.return_value = [
            Document(content="test content", name="doc1"),
        ]
        mocker.patch("knowledge_base.get_knowledge", return_value=mock_kb)

        from knowledge_base import search
        results = search("multi-agent systems")

        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["content"] == "test content"

    def test_passes_num_documents(self, mocker):
        mock_kb = MagicMock()
        mock_kb.search.return_value = []
        mocker.patch("knowledge_base.get_knowledge", return_value=mock_kb)

        from knowledge_base import search
        search("test query", n_results=10)

        mock_kb.search.assert_called_once_with("test query", max_results=10)
