# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""
MyRefereeAI — Q21G League Referee Implementation.

Uses Gemini (via gemini_client) for LLM inference and
Agno RAG (via knowledge_base) for accurate question answering.

Book: Section 4.3 of MCP Architecture book
Strategy: Miller's Law (chunking) -> association word "chunk"
"""
import difflib
from typing import Any, Dict

from q21_referee import RefereeAI
import gemini_client
import knowledge_base
from book_config import (
    BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD,
    ACTUAL_ASSOCIATION_WORD, OPENING_SENTENCE,
    FALLBACK_SENTENCE_FEEDBACK, FALLBACK_WORD_FEEDBACK,
)


class MyRefereeAI(RefereeAI):
    """Referee AI using Gemini + Agno RAG. Paragraph: MCP book section 4.3."""

    def __init__(self, scenario: dict = None) -> None:
        self._opening_sentence = scenario["opening_sentence"] if scenario else OPENING_SENTENCE
        self._actual_word = scenario["actual_association_word"] if scenario else ACTUAL_ASSOCIATION_WORD
        self._book_name = scenario.get("book_name", BOOK_NAME) if scenario else BOOK_NAME
        self._book_hint = scenario.get("book_hint", BOOK_HINT) if scenario else BOOK_HINT
        self._association_word = scenario.get("association_word", ASSOCIATION_WORD) if scenario else ASSOCIATION_WORD
        knowledge_base.ensure_indexed()

    def get_warmup_question(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        return {"warmup_question":
                "How many items can the average human hold in short-term memory?"}

    def get_round_start_info(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        return {"book_name": self._book_name, "book_hint": self._book_hint,
                "association_word": self._association_word}

    def get_answers(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        dynamic = ctx.get("dynamic", ctx)
        questions = dynamic.get("questions", [])
        answers = []
        for q in questions:
            answers.append({"question_number": q["question_number"],
                            "answer": self._answer_question(q)})
        return {"answers": answers}

    def get_score_feedback(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        dynamic = ctx.get("dynamic", ctx)
        guess = dynamic["player_guess"]
        scores = gemini_client.generate_json(self._build_score_prompt(guess))
        if not self._valid_scores(scores):
            scores = self._fallback_scores(guess)
        return self._build_response(scores)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _answer_question(self, q: dict) -> str:
        context = knowledge_base.search(q['question_text'], n_results=4)
        ctx_text = " ".join(r["content"] for r in context)
        opts = q.get("options", {})
        prompt = (
            f'Answer based on this paragraph: "{self._opening_sentence}"\n'
            f'Context: {ctx_text}\n\n'
            f'Question: {q["question_text"]}\n'
            f'A: {opts.get("A","")}  B: {opts.get("B","")}  '
            f'C: {opts.get("C","")}  D: {opts.get("D","")}\n'
            f'Answer A/B/C/D if determinable from the sentence or context. '
            f'Use "Not Relevant" ONLY if completely absent from both.'
        )
        try:
            text = gemini_client.generate(prompt)
            for ch in text:
                if ch in "ABCD":
                    return ch
            return "Not Relevant"
        except Exception:
            return "Not Relevant"

    def _build_score_prompt(self, guess: dict) -> str:
        return (
            f'Score a player guess for the Q21 game. '
            f'Return ONLY valid JSON with exactly these keys.\n\n'
            f'ACTUAL opening sentence: "{self._opening_sentence}"\n'
            f'PLAYER opening sentence: "{guess.get("opening_sentence", "")}"\n'
            f'Player sentence justification: "{guess.get("sentence_justification", "")}"\n\n'
            f'ACTUAL association word: "{self._actual_word}"\n'
            f'PLAYER association word: "{guess.get("associative_word", "")}"\n'
            f'Player word justification: "{guess.get("word_justification", "")}"\n\n'
            f'If the player sentence is semantically equivalent but in a different '
            f'language, award partial credit proportional to conceptual accuracy.\n'
            f'Score each item 0-100. Return ONLY valid JSON:\n'
            f'{{"opening_sentence_score": <int 0-100>,'
            f'"sentence_justification_score": <int 0-100>,'
            f'"associative_word_score": <int 0-100>,'
            f'"word_justification_score": <int 0-100>,'
            f'"opening_sentence_feedback": "<150-200 words of feedback>",'
            f'"associative_word_feedback": "<150-200 words of feedback>"}}'
        )

    def _valid_scores(self, s: dict) -> bool:
        required = ["opening_sentence_score", "sentence_justification_score",
                    "associative_word_score", "word_justification_score",
                    "opening_sentence_feedback", "associative_word_feedback"]
        return all(k in s for k in required)

    def _fallback_scores(self, guess: dict) -> dict:
        def norm(t): return t.lower().strip()
        sent = difflib.SequenceMatcher(
            None, norm(self._opening_sentence),
            norm(guess.get("opening_sentence", ""))).ratio() * 100
        word = 100.0 if norm(self._actual_word) == norm(
            guess.get("associative_word", "")) else 0.0
        return {"opening_sentence_score": round(sent, 2),
                "sentence_justification_score": 0.0,
                "associative_word_score": word,
                "word_justification_score": 0.0,
                "opening_sentence_feedback": FALLBACK_SENTENCE_FEEDBACK,
                "associative_word_feedback": FALLBACK_WORD_FEEDBACK}

    def _build_response(self, s: dict) -> dict:
        private = (s["opening_sentence_score"] * 0.5
                   + s["sentence_justification_score"] * 0.2
                   + s["associative_word_score"] * 0.2
                   + s["word_justification_score"] * 0.1)
        return {
            "league_points": self._score_to_league_points(private),
            "private_score": round(private, 2),
            "breakdown": {k: s[k] for k in [
                "opening_sentence_score", "sentence_justification_score",
                "associative_word_score", "word_justification_score"]},
            "feedback": {
                "opening_sentence": s["opening_sentence_feedback"],
                "associative_word": s["associative_word_feedback"]},
        }

    @staticmethod
    def _score_to_league_points(score: float) -> int:
        if score >= 80:
            return 3
        if score >= 60:
            return 2
        if score >= 40:
            return 1
        return 0
