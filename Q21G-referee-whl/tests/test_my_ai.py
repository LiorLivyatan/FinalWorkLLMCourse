# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for MyRefereeAI — all 4 callbacks."""
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add examples/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

from my_ai import MyRefereeAI
from book_config import BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD

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


# Callback 1
def test_warmup_returns_question():
    ai = MyRefereeAI()
    result = ai.get_warmup_question(make_warmup_ctx())
    assert "warmup_question" in result and len(result["warmup_question"]) > 0


def test_warmup_wrapped_and_raw():
    ai = MyRefereeAI()
    r1 = ai.get_warmup_question(make_warmup_ctx(True))
    r2 = ai.get_warmup_question(make_warmup_ctx(False))
    assert r1["warmup_question"] == r2["warmup_question"]


# Callback 2
def test_round_start_returns_book_info():
    ai = MyRefereeAI()
    result = ai.get_round_start_info(make_round_ctx())
    assert result["book_name"] == BOOK_NAME
    assert result["book_hint"] == BOOK_HINT
    assert result["association_word"] == ASSOCIATION_WORD


def test_round_start_wrapped_and_raw():
    ai = MyRefereeAI()
    assert ai.get_round_start_info(make_round_ctx(True)) == ai.get_round_start_info(make_round_ctx(False))


# Callback 3
def test_answers_happy_path():
    ai = MyRefereeAI()
    with patch("gemini_client.generate", return_value="B"), \
         patch("knowledge_base.search", return_value=[]):
        result = ai.get_answers(make_answers_ctx(make_questions(3)))
    assert len(result["answers"]) == 3
    for a in result["answers"]:
        assert a["answer"] in ("A", "B", "C", "D", "Not Relevant")


def test_answers_partial_failure_continues():
    ai = MyRefereeAI()
    call_count = [0]
    def side_effect(prompt):
        call_count[0] += 1
        if call_count[0] == 2:
            raise Exception("API error")
        return "C"
    with patch("gemini_client.generate", side_effect=side_effect), \
         patch("knowledge_base.search", return_value=[]):
        result = ai.get_answers(make_answers_ctx(make_questions(3)))
    answers = {a["question_number"]: a["answer"] for a in result["answers"]}
    assert answers[1] == "C"
    assert answers[2] == "Not Relevant"
    assert answers[3] == "C"


def test_answers_wrapped_and_raw():
    ai = MyRefereeAI()
    with patch("gemini_client.generate", return_value="A"), \
         patch("knowledge_base.search", return_value=[]):
        r1 = ai.get_answers(make_answers_ctx(make_questions(2), True))
        r2 = ai.get_answers(make_answers_ctx(make_questions(2), False))
    assert len(r1["answers"]) == len(r2["answers"])


# Callback 4
def test_score_happy_path():
    ai = MyRefereeAI()
    with patch("gemini_client.generate_json", return_value=VALID_SCORES):
        result = ai.get_score_feedback(make_score_ctx())
    assert result["league_points"] == 3
    assert isinstance(result["private_score"], float)
    assert set(result["breakdown"].keys()) == {
        "opening_sentence_score", "sentence_justification_score",
        "associative_word_score", "word_justification_score"}
    assert set(result["feedback"].keys()) == {"opening_sentence", "associative_word"}


def test_score_llm_failure_uses_fallback():
    ai = MyRefereeAI()
    with patch("gemini_client.generate_json", return_value={}):
        result = ai.get_score_feedback(make_score_ctx())
    assert "league_points" in result
    assert result["breakdown"]["sentence_justification_score"] == 0.0
    assert result["breakdown"]["word_justification_score"] == 0.0


def test_score_wrapped_and_raw():
    ai = MyRefereeAI()
    with patch("gemini_client.generate_json", return_value=VALID_SCORES):
        r1 = ai.get_score_feedback(make_score_ctx(True))
        r2 = ai.get_score_feedback(make_score_ctx(False))
    assert r1["league_points"] == r2["league_points"]


@pytest.mark.parametrize("score,pts", [
    (80.0, 3), (79.9, 2), (60.0, 2), (59.9, 1), (40.0, 1), (39.9, 0)
])
def test_league_points_boundaries(score, pts):
    assert MyRefereeAI._score_to_league_points(score) == pts
