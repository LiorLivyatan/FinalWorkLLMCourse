# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for gemini_client — mirrors player package pattern."""
import importlib.util
import pathlib
from unittest.mock import MagicMock, patch


def load_gemini_client(monkeypatch):
    """Load gemini_client from examples/ with mocked google.genai."""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.text = "hello"
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client_instance):
        spec = importlib.util.spec_from_file_location(
            "gemini_client_test",
            pathlib.Path(__file__).parent.parent / "examples" / "gemini_client.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod._client = mock_client_instance
    return mod


def test_generate_calls_gemini(monkeypatch):
    mod = load_gemini_client(monkeypatch)
    result = mod.generate("test prompt")
    assert mod._client.models.generate_content.called
    assert result == "hello"


def test_generate_json_parses_valid_json(monkeypatch):
    mod = load_gemini_client(monkeypatch)
    mod._client.models.generate_content.return_value.text = '{"score": 90}'
    result = mod.generate_json("test prompt")
    assert result == {"score": 90}


def test_generate_json_handles_code_fence(monkeypatch):
    mod = load_gemini_client(monkeypatch)
    mod._client.models.generate_content.return_value.text = '```json\n{"a": 1}\n```'
    result = mod.generate_json("test prompt")
    assert result == {"a": 1}


def test_generate_json_returns_empty_on_bad_json(monkeypatch):
    mod = load_gemini_client(monkeypatch)
    mod._client.models.generate_content.return_value.text = "not json"
    result = mod.generate_json("test prompt")
    assert result == {}
