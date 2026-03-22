# Area: Player AI
# PRD: docs/prd-player-ai.md
"""Helper utilities for MyPlayerAI — validation and fallback logic."""


def validate_guess(result: dict) -> dict:
    """Ensure all required fields exist with valid values."""
    defaults = {
        "opening_sentence": "Unable to determine the opening sentence.",
        "sentence_justification": " ".join(["analysis"] * 36),
        "associative_word": "unknown",
        "word_justification": " ".join(["reasoning"] * 36),
        "confidence": 0.5,
    }
    for key, default in defaults.items():
        if key not in result or not result[key]:
            result[key] = default
    result["confidence"] = float(result.get("confidence", 0.5))
    result["confidence"] = max(0.0, min(1.0, result["confidence"]))
    return result


def fallback_questions(book_name: str) -> list[dict]:
    """Return generic questions if LLM fails to produce valid JSON."""
    return [
        {
            "question_number": i,
            "question_text": f"Question {i} about {book_name}?",
            "options": {"A": "Yes", "B": "No", "C": "Partially", "D": "N/A"},
        }
        for i in range(1, 21)
    ]
