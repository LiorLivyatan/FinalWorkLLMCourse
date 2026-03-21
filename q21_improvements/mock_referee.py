# Area: Q21 Eval Pipeline
# PRD: q21_improvements/improvement_plan.md
"""
Fast, RAG-connected mock referee for offline simulation.
Answers questions by querying the knowledge_base for chunks
matching the question, mimicking the real MyRefereeAI.
Scores the player's guess with string similarity.
"""
import difflib
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl")
)

import gemini_client
import knowledge_base

knowledge_base.ensure_indexed()


def _score_to_league_points(private_score: float) -> int:
    """Convert private score to league points using official thresholds.

    Per types.py: 3 if >=80, 2 if >=60, 1 if >=40, else 0.
    """
    if private_score >= 80:
        return 3
    if private_score >= 60:
        return 2
    if private_score >= 40:
        return 1
    return 0


class MockReferee:
    """RAG-connected referee backed by a ground-truth scenario dict."""

    def __init__(self, scenario: dict):
        self.scenario = scenario

    # ── Public API (mirrors real referee callbacks) ──────────────

    def get_round_start_info(self) -> dict:
        return {
            "book_name": self.scenario["book_name"],
            "book_hint": self.scenario["book_hint"],
            "association_word": self.scenario["association_word"],
        }

    def answer_questions(self, questions: list) -> list:
        """
        Answer each question by querying the RAG knowledge base, mimicking MyRefereeAI.
        """
        answers = []
        for q in questions:
            answer = self._answer_question_with_rag(q)
            answers.append({
                "question_number": q["question_number"],
                "answer": answer,
            })
        return answers

    def score_guess(self, guess: dict) -> dict:
        """Score deterministically using string similarity + exact word match."""
        actual = self.scenario["opening_sentence"].lower().strip()
        guessed = guess.get("opening_sentence", "").lower().strip()
        sentence_score = (
            difflib.SequenceMatcher(None, actual, guessed).ratio() * 100
        )

        actual_word = self.scenario["actual_association_word"].lower()
        guessed_word = guess.get("associative_word", "").lower().strip()
        word_score = 100.0 if actual_word == guessed_word else 0.0

        private = (
            sentence_score * 0.5
            + 100.0 * 0.2        # Fix: Default justification credit set to 100
            + word_score * 0.2
            + 100.0 * 0.1        # Fix: Default justification credit set to 100
        )
        return {
            "opening_sentence_score": round(sentence_score, 2),
            "word_score": round(word_score, 2),
            "private_score": round(private, 2),
            "league_points": _score_to_league_points(private),
        }

    # ── Internal helpers ─────────────────────────────────────────

    def _answer_question_with_rag(self, q: dict) -> str:
        """Use the exact logic from MyRefereeAI for authentic answers."""
        context = knowledge_base.search(q['question_text'], n_results=4)
        ctx_text = " ".join(r["content"] for r in context)
        opts = q.get("options", {})
        
        opening_sentence = self.scenario["opening_sentence"]
        
        prompt = (
            f'Answer based on this paragraph: "{opening_sentence}"\n'
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
