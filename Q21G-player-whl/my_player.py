# Area: Player AI
# PRD: docs/prd-player-ai.md
"""
My Q21 Player Implementation.

Uses Gemini for inference and ChromaDB-backed knowledge base
for retrieving real opening sentences from course material.
"""
from q21_player import PlayerAI
from gemini_client import generate, generate_json
from knowledge_base import ensure_indexed, search


class MyPlayerAI(PlayerAI):
    """Player AI that uses RAG to find real opening sentences."""

    def __init__(self):
        ensure_indexed()

    def get_warmup_answer(self, ctx: dict) -> dict:
        question = ctx["dynamic"]["warmup_question"]
        prompt = (
            f"Solve this math question. Reply with ONLY the numeric "
            f"answer, nothing else.\n\nQuestion: {question}"
        )
        answer = generate(prompt).strip()
        return {"answer": answer}

    def get_questions(self, ctx: dict) -> dict:
        book_name = ctx["dynamic"]["book_name"]
        book_hint = ctx["dynamic"].get("book_hint", "")
        association_word = ctx["dynamic"].get("association_word", "")

        prompt = _build_questions_prompt(book_name, book_hint, association_word)
        result = generate_json(prompt)

        questions = result.get("questions", [])
        if len(questions) != 20:
            questions = _fallback_questions(book_name)
        return {"questions": questions}

    def get_guess(self, ctx: dict) -> dict:
        book_name = ctx["dynamic"].get("book_name", "Unknown")
        book_hint = ctx["dynamic"].get("book_hint", "")
        association_word = ctx["dynamic"].get("association_word", "")
        answers = ctx["dynamic"]["answers"]

        # Search knowledge base for candidate paragraphs
        query = f"{book_name} {book_hint} {association_word}"
        candidates = search(query, n_results=5)
        candidates_text = "\n---\n".join(
            c["content"] for c in candidates
        )

        prompt = _build_guess_prompt(
            book_name, book_hint, association_word,
            answers, candidates_text,
        )
        result = generate_json(prompt)
        return _validate_guess(result)

    def on_score_received(self, ctx: dict) -> None:
        points = ctx["dynamic"].get("league_points", 0)
        match_id = ctx["dynamic"].get("match_id", "unknown")
        print(f"Game {match_id} complete! Scored {points} points.")


# ── Prompt builders ────────────────────────────────────────────


def _build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    # TODO: This is the strategic prompt — see note below.
    return f"""You are playing a 21-questions game about a book's opening sentence.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Generate exactly 20 multiple-choice questions to identify the opening sentence.
Structure your questions in 3 tiers:
- Questions 1-7: Identify the CHAPTER or broad TOPIC area
- Questions 8-14: Narrow down the PARAGRAPH theme and structure
- Questions 15-20: Target SPECIFIC words, phrases, or sentence patterns

Each question must have 4 options labeled A, B, C, D.

Reply with ONLY valid JSON in this exact format:
{{"questions": [
  {{"question_number": 1, "question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}}},
  ...
]}}"""


def _build_guess_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict], candidates_text: str,
) -> str:
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""You are guessing a book's opening sentence based on Q&A clues.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Answers to your 20 questions:
{answers_str}

Candidate paragraphs from the course material:
{candidates_text}

Based on all evidence, identify the EXACT opening sentence from the
candidates above. If none match perfectly, construct the best guess.

Reply with ONLY valid JSON:
{{"opening_sentence": "...",
  "sentence_justification": "... (at least 35 words explaining your reasoning)",
  "associative_word": "... (one word thematically related to the book)",
  "word_justification": "... (at least 35 words explaining your word choice)",
  "confidence": 0.75}}"""


def _validate_guess(result: dict) -> dict:
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


def _fallback_questions(book_name: str) -> list[dict]:
    """Return generic questions if LLM fails to produce valid JSON."""
    return [
        {
            "question_number": i,
            "question_text": f"Question {i} about {book_name}?",
            "options": {"A": "Yes", "B": "No", "C": "Partially", "D": "N/A"},
        }
        for i in range(1, 21)
    ]
