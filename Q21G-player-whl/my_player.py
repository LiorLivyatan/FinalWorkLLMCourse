# Area: Player AI
# PRD: docs/prd-player-ai.md
"""My Q21 Player — HyDE RAG + Orthogonal Questions + CoT Deliberation."""
from q21_player import PlayerAI
from openai_client import generate, generate_json
from knowledge_base import ensure_indexed, search
from prompts import (
    build_questions_prompt,
    build_mp_hyde_prompt,
    build_keyword_extraction_prompt,
    build_guess_prompt,
)
from candidate_filter import deterministic_filter, llm_filter
from council import council_deliberate
from player_helpers import validate_guess, fallback_questions

try:
    from q21_improvements.phase_logger import PhaseLogger
except ImportError:
    from phase_logger import PhaseLogger


class MyPlayerAI(PlayerAI):
    """Player AI that uses RAG to find real opening sentences.

    Stores questions between callbacks because the real game only
    passes answer letters (A/B/C/D) back — not the question texts.
    """

    def __init__(self):
        ensure_indexed()
        self._last_questions = []
        self.logger = None

    def _log(self, phase, data):
        if self.logger:
            self.logger.log_phase(phase, data)

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
            questions = fallback_questions(book_name)
        self._last_questions = questions
        self.logger = PhaseLogger(book_name)
        self._log("phase1_questions", questions)
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

        self._log("phase2_answers", enriched)

        # ── Step 1: Multi-Perspective HyDE (temp=0.4 for diversity) ─
        mp_prompt = build_mp_hyde_prompt(
            book_name, book_hint, association_word, enriched)
        mp_result = generate_json(mp_prompt, temperature=0.4)
        paragraphs = mp_result.get("paragraphs", [])
        if not paragraphs:
            paragraphs = [f"{book_name} {book_hint}"]
        self._log("phase3_queries", paragraphs)

        # ── Step 2: Stratified RAG search ─────────────────────────
        # Probe A: HyDE semantic (3 correlated queries)
        all_results = []
        for p in paragraphs:
            all_results.extend(search(p, n_results=5))
        # Probe B: keyword extraction (independent, lexical region)
        kw_prompt = build_keyword_extraction_prompt(book_hint, association_word)
        kw = generate_json(kw_prompt)
        heb_kw = kw.get("hebrew_keywords", "")
        eng_kw = kw.get("english_keywords", "")
        if heb_kw:
            all_results.extend(search(heb_kw, n_results=5))
        if eng_kw:
            all_results.extend(search(eng_kw, n_results=3))
        # Probe C: association word lateral search
        all_results.extend(search(
            f"{association_word} {book_name}", n_results=3))

        # Deduplicate and merge
        seen = set()
        candidates = []
        for c in all_results:
            key = c["content"][:100]
            if key not in seen:
                seen.add(key)
                candidates.append(c)

        top_candidates = candidates[:10]
        self._log("phase4_candidates",
                  [{"content": c["content"][:150]} for c in top_candidates])

        # ── Step 3: Hybrid Filter ─────────────────────────────────
        filtered = deterministic_filter(top_candidates, enriched)
        filtered = llm_filter(filtered, enriched)
        self._log("phase5_filter",
                  [{"content": c["content"][:150]} for c in filtered])

        # ── Step 4: Two-Model Council ─────────────────────────────
        council_result = council_deliberate(filtered, enriched)
        self._log("phase6_council", council_result)
        best_text = council_result.get("best_paragraph_text", "")

        # ── Step 5: Final guess ───────────────────────────────────
        prompt = build_guess_prompt(
            book_name, book_hint, association_word, answers, best_text)
        result = generate_json(prompt)
        validated = validate_guess(result)
        self._log("final_guess", validated)
        return validated

    def on_score_received(self, ctx: dict) -> None:
        points = ctx["dynamic"].get("league_points", 0)
        match_id = ctx.get("service", {}).get("match_id", "unknown")
        print(f"Game {match_id} complete! Scored {points} points.")
