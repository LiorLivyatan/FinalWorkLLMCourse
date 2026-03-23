import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))

import inspect
from gemini_client import generate
from candidate_filter import deterministic_filter

CANDIDATE_WITH_NUMBERS = {"content": "מגבלת150שורות לקובץ היא לא מספר שרירותי."}
CANDIDATE_NO_NUMBERS = {"content": "המערכת מבוססת על הפרדה ברורה בין שכבות."}

ENRICHED_NUMBERS = [
    {"question_number": 6, "answer": "B", "question_text": "Numbers?",
     "options": {"A": "No numbers", "B": "Contains numeric thresholds",
                 "C": "Only dates", "D": "None of these apply"}},
]
ENRICHED_NO_SIGNAL = [
    {"question_number": 1, "answer": "D", "question_text": "Format?",
     "options": {"A": "List", "B": "Prose", "C": "Code", "D": "None of these apply"}},
]

def test_gemini_generate_accepts_model_param():
    sig = inspect.signature(generate)
    assert "model" in sig.parameters

def test_filter_ranks_matching_candidate_first():
    """Candidate with numbers should be ranked first (highest score)."""
    result = deterministic_filter(
        [CANDIDATE_NO_NUMBERS, CANDIDATE_WITH_NUMBERS], ENRICHED_NUMBERS)
    assert result[0] == CANDIDATE_WITH_NUMBERS

def test_filter_skips_when_answer_is_d():
    both = [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS]
    result = deterministic_filter(both, ENRICHED_NO_SIGNAL)
    assert len(result) == 2

def test_filter_never_returns_empty():
    result = deterministic_filter([CANDIDATE_NO_NUMBERS], ENRICHED_NUMBERS)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Task 3: LLM filter prompt builder
# ---------------------------------------------------------------------------

def test_llm_filter_prompt_builder():
    from candidate_filter import _build_filter_prompt
    CANDIDATE_WITH_NUMBERS = {"content": "מגבלת150שורות לקובץ היא לא מספר שרירותי."}
    CANDIDATE_NO_NUMBERS = {"content": "המערכת מבוססת על הפרדה ברורה בין שכבות."}
    ENRICHED_NUMBERS = [
        {"question_number": 6, "answer": "B", "question_text": "Numbers?",
         "options": {"A": "No numbers", "B": "Contains numeric thresholds",
                     "C": "Only dates", "D": "None of these apply"}},
    ]
    prompt = _build_filter_prompt(
        [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS], ENRICHED_NUMBERS)
    assert "Candidate 0:" in prompt
    assert "Candidate 1:" in prompt
    assert "Contains numeric thresholds" in prompt


# ---------------------------------------------------------------------------
# Task 4: Two-model council — resolve_council
# ---------------------------------------------------------------------------

from council import resolve_council

def test_council_agree():
    gpt = {"best_candidate_index": 0, "confidence": 8}
    gem = {"best_candidate_index": 0, "confidence": 7}
    assert resolve_council(gpt, gem) == 0

def test_council_disagree_higher_confidence_wins():
    gpt = {"best_candidate_index": 0, "confidence": 6}
    gem = {"best_candidate_index": 1, "confidence": 9}
    assert resolve_council(gpt, gem) == 1

def test_council_tied_confidence_gpt_wins():
    gpt = {"best_candidate_index": 0, "confidence": 8}
    gem = {"best_candidate_index": 1, "confidence": 8}
    assert resolve_council(gpt, gem) == 0
