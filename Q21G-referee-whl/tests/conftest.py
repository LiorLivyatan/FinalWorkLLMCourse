# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Session-scoped patch so gemini_client can be imported without a real API key."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure examples/ is on the path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

# Set a fake key so genai.Client() doesn't raise at import time
os.environ.setdefault("GOOGLE_API_KEY", "fake-key-for-tests")

# Patch google.genai.Client before gemini_client is imported
_mock_client = MagicMock()
_mock_response = MagicMock()
_mock_response.text = "A"
_mock_client.models.generate_content.return_value = _mock_response

_patcher = patch("google.genai.Client", return_value=_mock_client)
_patcher.start()

from book_config import BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD  # noqa: E402

VALID_SCORES = {
    "opening_sentence_score": 85.0,
    "sentence_justification_score": 70.0,
    "associative_word_score": 100.0,
    "word_justification_score": 80.0,
    "opening_sentence_feedback": "Good attempt.",
    "associative_word_feedback": "Correct word!",
}


def make_warmup_ctx(wrapped=True):
    data = {"round_number": 1, "game_id": "0101001"}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_round_ctx(wrapped=True):
    data = {"round_number": 1,
            "player_a": {"id": "p1", "email": "a@x.com", "warmup_answer": "7"},
            "player_b": {"id": "p2", "email": "b@x.com", "warmup_answer": "six"}}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_questions(n=3):
    return [{"question_number": i+1, "question_text": f"Q{i+1}?",
             "options": {"A": "a", "B": "b", "C": "c", "D": "d"}} for i in range(n)]


def make_answers_ctx(questions=None, wrapped=True):
    data = {"book_name": BOOK_NAME, "book_hint": BOOK_HINT,
            "association_word": ASSOCIATION_WORD,
            "questions": questions or make_questions()}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_score_ctx(wrapped=True):
    data = {"book_name": BOOK_NAME, "book_hint": BOOK_HINT,
            "association_word": ASSOCIATION_WORD,
            "actual_opening_sentence": None,
            "actual_associative_word": None,
            "player_guess": {
                "opening_sentence": "The 150-line limit is not arbitrary.",
                "sentence_justification": "Based on Miller's Law.",
                "associative_word": "seven",
                "word_justification": "7 items in memory.",
                "confidence": 0.9}}
    return {"dynamic": data, "service": {}} if wrapped else data
