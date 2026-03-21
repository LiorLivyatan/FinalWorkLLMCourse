# Area: Q21 Eval Pipeline
# PRD: q21_improvements/improvement_plan.md
"""
TDD tests for MockReferee and _score_to_league_points.

Run:  python -m pytest q21_improvements/test_simulation.py -v
No API keys or network required.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from q21_improvements.mock_referee import MockReferee, _score_to_league_points
from q21_improvements.scenarios import SCENARIO_1, ALL_SCENARIOS


# ── Fixtures ─────────────────────────────────────────────────────

SIMPLE_SCENARIO = {
    "book_name": "Test Book",
    "book_hint": "A hint about programming limits",
    "association_word": "memory",
    "actual_association_word": "chunk",
    "opening_sentence": "The 150-line limit per file is not an arbitrary number.",
    "warmup_answer": "7",
}

SAMPLE_QUESTIONS = [
    {"question_number": 1, "question_text": "Numeric limit?",
     "options": {"A": "limit", "B": "color", "C": "weather", "D": "music"}},
    {"question_number": 2, "question_text": "Abstract?",
     "options": {"A": "cloud", "B": "arbitrary", "C": "ocean", "D": "stone"}},
    {"question_number": 3, "question_text": "Programming?",
     "options": {"A": "cooking", "B": "dance", "C": "programming", "D": "sport"}},
    {"question_number": 4, "question_text": "No match?",
     "options": {"A": "xyz", "B": "qrs", "C": "tuv", "D": "opq"}},
]


# ── Tests: answer_questions() ────────────────────────────────────

def test_answer_matches_sentence_word():
    answers = MockReferee(SIMPLE_SCENARIO).answer_questions([SAMPLE_QUESTIONS[0]])
    assert answers[0]["answer"] == "A"

def test_answer_matches_hint_word():
    answers = MockReferee(SIMPLE_SCENARIO).answer_questions([SAMPLE_QUESTIONS[2]])
    assert answers[0]["answer"] == "C"

def test_answer_falls_back_to_not_relevant():
    answers = MockReferee(SIMPLE_SCENARIO).answer_questions([SAMPLE_QUESTIONS[3]])
    assert answers[0]["answer"] == "Not Relevant"

def test_answer_preserves_question_numbers():
    answers = MockReferee(SIMPLE_SCENARIO).answer_questions(SAMPLE_QUESTIONS)
    assert [a["question_number"] for a in answers] == [1, 2, 3, 4]


# ── Tests: score_guess() ─────────────────────────────────────────

def test_exact_match_scores_100():
    guess = {"opening_sentence": SIMPLE_SCENARIO["opening_sentence"],
             "associative_word": "chunk"}
    result = MockReferee(SIMPLE_SCENARIO).score_guess(guess)
    assert result["opening_sentence_score"] == 100.0
    assert result["word_score"] == 100.0
    assert result["private_score"] > 90

def test_wrong_word_scores_zero():
    guess = {"opening_sentence": SIMPLE_SCENARIO["opening_sentence"],
             "associative_word": "memory"}
    assert MockReferee(SIMPLE_SCENARIO).score_guess(guess)["word_score"] == 0.0

def test_partial_sentence_gives_partial_score():
    guess = {"opening_sentence": "The limit is not arbitrary.", "associative_word": "chunk"}
    score = MockReferee(SIMPLE_SCENARIO).score_guess(guess)["opening_sentence_score"]
    assert 0 < score < 100

def test_empty_guess_scores_zero():
    result = MockReferee(SIMPLE_SCENARIO).score_guess({"opening_sentence": "", "associative_word": ""})
    assert result["opening_sentence_score"] == 0.0
    assert result["word_score"] == 0.0


# ── Tests: _score_to_league_points() ─────────────────────────────

def test_points_3_at_90():
    assert _score_to_league_points(90.0) == 3
    assert _score_to_league_points(95.5) == 3

def test_points_2_at_80():
    assert _score_to_league_points(80.0) == 2
    assert _score_to_league_points(89.9) == 2

def test_points_1_at_60():
    assert _score_to_league_points(60.0) == 1
    assert _score_to_league_points(79.9) == 1

def test_points_0_below_60():
    assert _score_to_league_points(59.9) == 0
    assert _score_to_league_points(0.0) == 0


# ── Tests: Scenario integrity ────────────────────────────────────

def test_scenario_1_exact_sentence():
    assert SCENARIO_1["opening_sentence"] == "The 150-line limit per file is not an arbitrary number."

def test_scenario_1_words():
    assert SCENARIO_1["association_word"] == "memory"
    assert SCENARIO_1["actual_association_word"] == "chunk"

def test_at_least_3_scenarios():
    assert len(ALL_SCENARIOS) >= 3

def test_all_scenarios_have_required_fields():
    required = {"book_name", "book_hint", "association_word",
                "actual_association_word", "opening_sentence"}
    for s in ALL_SCENARIOS:
        assert required.issubset(s.keys()), f"Missing fields in {s.get('name','?')}"


def test_run_game_returns_required_keys():
    from q21_improvements.simulate_player_performance import run_game
    result = run_game(SCENARIO_1)
    required = {"name", "guessed", "actual", "word_guessed", "word_actual",
                "nr", "opening_sentence_score", "word_score", "private_score",
                "league_points"}
    assert required.issubset(result.keys())
