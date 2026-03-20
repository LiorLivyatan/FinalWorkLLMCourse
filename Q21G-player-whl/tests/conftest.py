# Area: Player AI Testing
# PRD: docs/prd-player-ai.md
"""Shared fixtures for player AI tests."""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env from project root (one level above Q21G-player-whl)
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: tests requiring real API keys and services"
    )


@pytest.fixture
def mock_gemini_response(mocker):
    """Mock google.genai client to return a controlled response."""
    mock_client = MagicMock()
    mocker.patch("gemini_client._client", mock_client)

    def set_response(text):
        mock_client.models.generate_content.return_value.text = text

    set_response("42")
    return set_response, mock_client


@pytest.fixture
def sample_ctx_warmup():
    return {"dynamic": {"warmup_question": "What is 6 * 7?"}}


@pytest.fixture
def sample_ctx_questions():
    return {
        "dynamic": {
            "book_name": "Introduction to Multi-Agent Systems",
            "book_hint": "Explores how autonomous agents coordinate and communicate",
            "association_word": "cooperation",
        }
    }


@pytest.fixture
def sample_ctx_guess():
    return {
        "dynamic": {
            "book_name": "Introduction to Multi-Agent Systems",
            "book_hint": "Explores how autonomous agents coordinate and communicate",
            "association_word": "cooperation",
            "answers": [
                {"question_number": i, "answer": "A"} for i in range(1, 21)
            ],
        }
    }


@pytest.fixture
def sample_ctx_score():
    return {
        "dynamic": {
            "league_points": 75,
            "match_id": "M001",
            "private_score": 72.5,
            "breakdown": {
                "opening_sentence_score": 80.0,
                "sentence_justification_score": 70.0,
                "associative_word_score": 60.0,
                "word_justification_score": 80.0,
            },
        }
    }
