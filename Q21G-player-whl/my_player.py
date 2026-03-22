# Area: Player AI
# PRD: docs/prd-player-ai.md
"""
My Q21 Player Implementation.

Uses Gemini for inference and ChromaDB-backed knowledge base
for retrieving real opening sentences from course material.

Strategy: HyDE RAG + Orthogonal Questions + CoT Deliberation.
"""
from q21_player import PlayerAI
from openai_client import generate, generate_json
from knowledge_base import ensure_indexed, search
from q21_improvements.phase_logger import PhaseLogger
from prompts import (
    build_questions_prompt,
    build_hyde_prompt,
    build_mp_hyde_prompt,
    build_deliberation_prompt,
    build_guess_prompt,
)


class MyPlayerAI(PlayerAI):
    """Player AI that uses RAG to find real opening sentences.

    Stores questions between callbacks because the real game only
    passes answer letters (A/B/C/D) back — not the question texts.
    """

    def __init__(self):
        ensure_indexed()
        self._last_questions = []  # stored for use in get_guess()
        self.logger = None

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

        prompt = build_questions_prompt(book_name, book_hint, association_word)
        result = generate_json(prompt)

        questions = result.get("questions", [])
        if len(questions) != 20:
            questions = _fallback_questions(book_name)
        self._last_questions = questions  # store for get_guess()
        
        self.logger = PhaseLogger(book_name)
        self.logger.log_phase("phase1_questions", questions)
        
        return {"questions": questions}

    def get_guess(self, ctx: dict) -> dict:
        book_name = ctx["dynamic"].get("book_name", "Unknown")
        book_hint = ctx["dynamic"].get("book_hint", "")
        association_word = ctx["dynamic"].get("association_word", "")
        answers = ctx["dynamic"]["answers"]

        # Enrich answers with stored question texts
        q_by_num = {q["question_number"]: q for q in self._last_questions}
        enriched = []
        for a in answers:
            q = q_by_num.get(a["question_number"], {})
            enriched.append({
                **a,
                "question_text": q.get("question_text", ""),
                "options": q.get("options", {}),
            })
            
        if self.logger:
            self.logger.log_phase("phase2_answers", enriched)

        # ── Step 1: Multi-Perspective HyDE ───────────────────────
        mp_prompt = build_mp_hyde_prompt(
            book_name, book_hint, association_word, enriched,
        )
        mp_result = generate_json(mp_prompt)
        paragraphs = mp_result.get("paragraphs", [])
        if not paragraphs:
            paragraphs = [f"{book_name} {book_hint}"]
            
        if self.logger:
            self.logger.log_phase("phase3_queries", paragraphs)

        # ── Step 2: RAG — search with all paragraphs ──────────────
        candidates_hyde = []
        for p in paragraphs:
            candidates_hyde.extend(search(p, n_results=5))
            
        candidates_orig = search(
            f"{book_name} {book_hint} {association_word}", n_results=3,
        )

        # Deduplicate and merge
        seen = set()
        candidates = []
        for c in candidates_hyde + candidates_orig:
            key = c["content"][:100]
            if key not in seen:
                seen.add(key)
                candidates.append(c)
                
        # Top 10 uniqueness check
        top_candidates = candidates[:10]
        candidates_text = "\n---\n".join(c["content"] for c in top_candidates)
        
        if self.logger:
            self.logger.log_phase("phase4_candidates", [{"content": c["content"][:150] + "..."} for c in top_candidates])

        # ── Step 3: CoT — deliberate on candidates ──────────────
        delib_prompt = build_deliberation_prompt(
            book_name, answers, candidates_text,
        )
        deliberation = generate_json(delib_prompt)
        
        if self.logger:
            self.logger.log_phase("phase5_deliberation", deliberation)
            
        best_text = deliberation.get("best_paragraph_text", candidates_text)

        # ── Step 4: Final guess from best candidate ──────────────
        prompt = build_guess_prompt(
            book_name, book_hint, association_word, answers, best_text,
        )
        result = generate_json(prompt)
        validated = _validate_guess(result)
        
        if self.logger:
            self.logger.log_phase("final_guess", validated)
            
        return validated

    def on_score_received(self, ctx: dict) -> None:
        points = ctx["dynamic"].get("league_points", 0)
        match_id = ctx.get("service", {}).get("match_id", "unknown")
        print(f"Game {match_id} complete! Scored {points} points.")


# ── Helpers ───────────────────────────────────────────────────────


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
