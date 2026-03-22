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

def test_filter_keeps_candidate_with_numbers():
    result = deterministic_filter(
        [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS], ENRICHED_NUMBERS)
    assert len(result) == 1
    assert result[0] == CANDIDATE_WITH_NUMBERS

def test_filter_skips_when_answer_is_d():
    both = [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS]
    result = deterministic_filter(both, ENRICHED_NO_SIGNAL)
    assert len(result) == 2

def test_filter_never_returns_empty():
    result = deterministic_filter([CANDIDATE_NO_NUMBERS], ENRICHED_NUMBERS)
    assert len(result) == 1
