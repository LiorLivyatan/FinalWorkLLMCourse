# Area: Player AI - Gemini Client
# PRD: docs/prd-player-ai.md
"""Unit tests for gemini_client module."""
import pytest
from unittest.mock import MagicMock


class TestGenerate:
    def test_returns_string(self, mock_gemini_response):
        from gemini_client import generate

        set_resp, _ = mock_gemini_response
        set_resp("Paris")
        result = generate("What is the capital of France?")
        assert isinstance(result, str)
        assert result == "Paris"

    def test_passes_prompt_to_model(self, mock_gemini_response):
        from gemini_client import generate

        _, mock_client = mock_gemini_response
        generate("test prompt")
        mock_client.models.generate_content.assert_called_once()
        call_kwargs = mock_client.models.generate_content.call_args[1]
        assert call_kwargs["contents"] == "test prompt"

    def test_model_id_from_env(self, mock_gemini_response, monkeypatch):
        monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
        _, mock_client = mock_gemini_response

        from gemini_client import generate
        generate("test")

        call_kwargs = mock_client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-test-model"

    def test_default_model_when_env_unset(self, mock_gemini_response, monkeypatch):
        monkeypatch.delenv("GEMINI_MODEL", raising=False)
        _, mock_client = mock_gemini_response

        from gemini_client import generate
        generate("test")

        call_kwargs = mock_client.models.generate_content.call_args[1]
        assert "gemini" in call_kwargs["model"].lower()


class TestGenerateJson:
    def test_returns_parsed_dict(self, mock_gemini_response):
        from gemini_client import generate_json

        set_resp, _ = mock_gemini_response
        set_resp('{"answer": "42"}')
        result = generate_json("What is 6*7?")
        assert isinstance(result, dict)
        assert result["answer"] == "42"

    def test_handles_markdown_code_block(self, mock_gemini_response):
        from gemini_client import generate_json

        set_resp, _ = mock_gemini_response
        set_resp('```json\n{"answer": "42"}\n```')
        result = generate_json("test")
        assert result["answer"] == "42"

    def test_returns_empty_dict_on_invalid_json(self, mock_gemini_response):
        from gemini_client import generate_json

        set_resp, _ = mock_gemini_response
        set_resp("not valid json at all")
        result = generate_json("test")
        assert result == {}
