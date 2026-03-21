# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for knowledge_base (mocked Agno)."""
import importlib.util
import pathlib
from unittest.mock import MagicMock, patch


def load_kb(mock_kb=None):
    """Load knowledge_base module with optional mock KB injected."""
    spec = importlib.util.spec_from_file_location(
        "knowledge_base",
        pathlib.Path(__file__).parent.parent / "examples" / "knowledge_base.py"
    )
    mod = importlib.util.module_from_spec(spec)
    with patch("agno.knowledge.knowledge.Knowledge"), \
         patch("agno.knowledge.embedder.google.GeminiEmbedder"), \
         patch("agno.vectordb.chroma.ChromaDb"):
        spec.loader.exec_module(mod)
    if mock_kb is not None:
        mod._knowledge = mock_kb
    return mod


def test_search_returns_list_of_dicts():
    mock_doc = MagicMock()
    mock_doc.content = "The 150-line limit is based on Miller's Law."
    mock_kb = MagicMock()
    mock_kb.search.return_value = [mock_doc]

    mod = load_kb(mock_kb=mock_kb)
    results = mod.search("150-line limit", n_results=1)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["content"] == "The 150-line limit is based on Miller's Law."


def test_search_propagates_error():
    mock_kb = MagicMock()
    mock_kb.search.side_effect = Exception("DB error")

    mod = load_kb(mock_kb=mock_kb)
    try:
        mod.search("anything")
        assert False, "Expected exception to propagate"
    except Exception as e:
        assert "DB error" in str(e)


def test_ensure_indexed_raises_on_missing_path(tmp_path, monkeypatch):
    monkeypatch.setenv("COURSE_MATERIAL_PATH", str(tmp_path / "nonexistent"))
    mock_kb = MagicMock()
    mod = load_kb(mock_kb=mock_kb)
    try:
        mod.ensure_indexed()
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass
    mock_kb.insert.assert_not_called()
