# Deliberation Pipeline Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve paragraph selection accuracy from 1-2/5 to 4-5/5 by adding a hybrid filter and two-model council to the player's deliberation pipeline.

**Architecture:** After RAG retrieval (10 candidates), a deterministic regex filter eliminates obvious mismatches (10→~6), then a cheap LLM enforces Q&A constraints (~6→2-3), then GPT-5.4 and Gemini 3.1 Pro independently deliberate on the survivors with confidence scores. The question prompt is also updated to adaptively allocate questions based on what the hint already reveals.

**Tech Stack:** Python 3.12, OpenAI SDK (GPT-5.4), Google GenAI SDK (Gemini 3.1 Flash + Pro), ChromaDB, pytest

**Spec:** `docs/superpowers/specs/2026-03-23-deliberation-improvements-design.md`

---

## File Structure

```
Q21G-player-whl/
├── candidate_filter.py    # NEW: deterministic + LLM filtering
├── council.py             # NEW: two-model council with confidence
├── gemini_client.py       # MODIFY: add model override parameter
├── prompts_questions.py   # NEW: split from prompts.py — question + HyDE prompts
├── prompts_deliberation.py# NEW: split from prompts.py — council, filter, guess prompts
├── prompts.py             # MODIFY: re-export hub (imports from both splits)
├── player_helpers.py      # NEW: split from my_player.py — _validate_guess, _fallback
├── my_player.py           # MODIFY: wire new phases, use split imports
└── openai_client.py       # READ-ONLY (council uses it as-is)

q21_improvements/
└── test_deliberation.py   # NEW: unit tests for filter + council
```

**Note on 150-line limit:** `prompts.py` (176 lines) and `my_player.py` (182 lines) both exceed the project's 150-line limit. This plan includes splitting them as part of the implementation:
- `prompts.py` → `prompts_questions.py` + `prompts_deliberation.py` + `prompts.py` (re-export hub)
- `my_player.py` → extract helpers into `player_helpers.py`

---

### Task 0: Split oversized files to meet 150-line limit

`prompts.py` (176 lines) and `my_player.py` (182 lines) both exceed the 150-line limit. Split them before adding new code.

**Files:**
- Create: `Q21G-player-whl/prompts_questions.py` (question + HyDE prompts)
- Create: `Q21G-player-whl/prompts_deliberation.py` (deliberation + guess prompts)
- Modify: `Q21G-player-whl/prompts.py` (re-export hub)
- Create: `Q21G-player-whl/player_helpers.py` (validate_guess, fallback_questions)
- Modify: `Q21G-player-whl/my_player.py` (import from player_helpers)

- [ ] **Step 1: Split prompts.py**

Move `build_questions_prompt`, `build_hyde_prompt`, `build_mp_hyde_prompt` into `prompts_questions.py`.
Move `format_answer` (rename from `_format_answer`), `build_deliberation_prompt`, `build_guess_prompt` into `prompts_deliberation.py`.
Make `prompts.py` a thin re-export hub that imports and re-exports everything from both files.

- [ ] **Step 2: Split my_player.py helpers**

Move `_validate_guess()` and `_fallback_questions()` into `player_helpers.py`.
Import them in `my_player.py`.

- [ ] **Step 3: Verify all files ≤150 lines**

Run: `wc -l Q21G-player-whl/prompts*.py Q21G-player-whl/my_player.py Q21G-player-whl/player_helpers.py`
Expected: All ≤150

- [ ] **Step 4: Run existing tests**

Run: `python -m pytest q21_improvements/test_simulation.py -v`
Expected: ALL PASSED (re-exports preserve the interface)

- [ ] **Step 5: Commit**

```bash
git add Q21G-player-whl/prompts*.py Q21G-player-whl/player_helpers.py Q21G-player-whl/my_player.py
git commit -m "refactor: split prompts.py and my_player.py to meet 150-line limit"
```

---

### Task 1: Add model override to gemini_client.py

The council and filter need to call Gemini with different models than the default flash-lite. Add a `model` parameter to both functions.

**Files:**
- Modify: `Q21G-player-whl/gemini_client.py`
- Test: `q21_improvements/test_deliberation.py`

- [ ] **Step 1: Write the failing test**

```python
# q21_improvements/test_deliberation.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))

def test_gemini_generate_accepts_model_param():
    """Verify generate() accepts a model keyword argument."""
    import inspect
    from gemini_client import generate
    sig = inspect.signature(generate)
    assert "model" in sig.parameters, "generate() must accept model param"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest q21_improvements/test_deliberation.py::test_gemini_generate_accepts_model_param -v`
Expected: FAIL — current `generate()` has no `model` param

- [ ] **Step 3: Add model override to gemini_client.py**

```python
def generate(prompt: str, model: str = None) -> str:
    model_id = model or os.getenv("GEMINI_MODEL", _DEFAULT_MODEL)
    response = _client.models.generate_content(
        model=model_id, contents=prompt,
    )
    return response.text


def generate_json(prompt: str, model: str = None) -> dict:
    raw = generate(prompt, model=model)
    return _parse_json(raw)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest q21_improvements/test_deliberation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Q21G-player-whl/gemini_client.py q21_improvements/test_deliberation.py
git commit -m "feat: add model override param to gemini_client"
```

---

### Task 2: Build deterministic candidate filter

Programmatic elimination of candidates that violate hard Q&A constraints. Zero LLM calls.

**Files:**
- Create: `Q21G-player-whl/candidate_filter.py`
- Test: `q21_improvements/test_deliberation.py`

- [ ] **Step 1: Write the failing tests**

Add to `q21_improvements/test_deliberation.py`:

```python
from candidate_filter import deterministic_filter

CANDIDATE_WITH_NUMBERS = {"content": "מגבלת150שורות לקובץ היא לא מספר שרירותי."}
CANDIDATE_NO_NUMBERS = {"content": "המערכת מבוססת על הפרדה ברורה בין שכבות."}
CANDIDATE_WITH_LIST = {"content": "1. קריאות\n2. אחריות יחידה\n3. מודולריות"}
CANDIDATE_WITH_CODE = {"content": "def hello():\n    return 'world'"}

ENRICHED_NUMBERS = [
    {"question_number": 6, "answer": "B", "question_text": "Numbers?",
     "options": {"A": "No numbers", "B": "Contains numeric thresholds",
                 "C": "Only dates", "D": "None of these apply"}},
]

ENRICHED_NO_SIGNAL = [
    {"question_number": 1, "answer": "D", "question_text": "Format?",
     "options": {"A": "List", "B": "Prose", "C": "Code", "D": "None of these apply"}},
]


def test_filter_keeps_candidate_with_numbers():
    result = deterministic_filter(
        [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS], ENRICHED_NUMBERS)
    assert len(result) == 1
    assert result[0] == CANDIDATE_WITH_NUMBERS


def test_filter_skips_when_answer_is_d():
    """D means 'None of these apply' — no signal, keep all."""
    both = [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS]
    result = deterministic_filter(both, ENRICHED_NO_SIGNAL)
    assert len(result) == 2


def test_filter_never_returns_empty():
    """Safety guard: if all would be eliminated, return all."""
    result = deterministic_filter(
        [CANDIDATE_NO_NUMBERS], ENRICHED_NUMBERS)
    assert len(result) == 1  # kept despite mismatch
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest q21_improvements/test_deliberation.py -v -k "filter"`
Expected: FAIL — `ModuleNotFoundError: No module named 'candidate_filter'`

- [ ] **Step 3: Implement candidate_filter.py**

```python
# Area: Player AI - Candidate Filter
# PRD: docs/superpowers/specs/2026-03-23-deliberation-improvements-design.md
"""Deterministic + LLM filtering of RAG candidates using Q&A constraints."""
import re
from typing import Optional


def _has_numbers(text: str) -> bool:
    return bool(re.search(r'\d{2,}', text))


def _has_list_markers(text: str) -> bool:
    return bool(re.search(r'^\s*[\d•\-\*]', text, re.MULTILINE))


def _has_code(text: str) -> bool:
    return bool(re.search(r'(def |class |import |for |if |return )', text))


def _has_figure_ref(text: str) -> bool:
    return 'איור' in text or 'figure' in text.lower() or 'Figure' in text


# Map: (block_index, selected_option_keyword) → check function
# Each returns True if candidate MATCHES the constraint
_CHECKS = {
    "numeric": _has_numbers,
    "thresholds": _has_numbers,
    "numbers": _has_numbers,
    "list": _has_list_markers,
    "numbered": _has_list_markers,
    "bulleted": _has_list_markers,
    "code": _has_code,
    "figure": _has_figure_ref,
    "diagram": _has_figure_ref,
}


def _extract_signals(enriched_answers: list) -> list:
    """Extract filterable signals from Q&A answers.

    Only uses answers where the selected option (A/B/C) contains
    a keyword we can check programmatically. Skips D answers.
    """
    signals = []
    for a in enriched_answers:
        if a["answer"] == "D" or a["answer"] == "Not Relevant":
            continue
        opts = a.get("options", {})
        selected_text = opts.get(a["answer"], "").lower()
        for keyword, check_fn in _CHECKS.items():
            if keyword in selected_text:
                signals.append(check_fn)
                break
    return signals


def deterministic_filter(
    candidates: list[dict],
    enriched_answers: list[dict],
) -> list[dict]:
    """Filter candidates using hard Q&A constraints. Never returns empty."""
    signals = _extract_signals(enriched_answers)
    if not signals:
        return candidates

    survivors = []
    for c in candidates:
        text = c["content"]
        passes = all(check(text) for check in signals)
        if passes:
            survivors.append(c)

    return survivors if survivors else candidates
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest q21_improvements/test_deliberation.py -v -k "filter"`
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add Q21G-player-whl/candidate_filter.py q21_improvements/test_deliberation.py
git commit -m "feat: deterministic candidate filter using Q&A constraints"
```

---

### Task 3: Add LLM elimination round to candidate_filter.py

A cheap Gemini call that enforces constraints the regex can't catch.

**Files:**
- Modify: `Q21G-player-whl/candidate_filter.py`
- Test: `q21_improvements/test_deliberation.py`

- [ ] **Step 1: Write the test**

Add to `q21_improvements/test_deliberation.py`:

```python
def test_llm_filter_prompt_builder():
    """Verify the LLM filter builds a valid prompt from candidates + answers."""
    from candidate_filter import _build_filter_prompt
    prompt = _build_filter_prompt(
        [CANDIDATE_WITH_NUMBERS, CANDIDATE_NO_NUMBERS],
        ENRICHED_NUMBERS,
    )
    assert "Candidate 0:" in prompt
    assert "Candidate 1:" in prompt
    assert "Contains numeric thresholds" in prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest q21_improvements/test_deliberation.py::test_llm_filter_prompt_builder -v`
Expected: FAIL

- [ ] **Step 3: Add _build_filter_prompt and llm_filter to candidate_filter.py**

```python
def _build_filter_prompt(candidates: list, enriched: list) -> str:
    """Build constraint-enforcement prompt for cheap LLM."""
    from prompts import format_answer
    answers_str = "\n".join(format_answer(a) for a in enriched)
    cands_str = "\n\n".join(
        f"Candidate {i}:\n{c['content'][:500]}"
        for i, c in enumerate(candidates)
    )
    return f"""You are a strict filter. Check each candidate paragraph
against these Q&A constraints about the target paragraph.

Q&A Evidence:
{answers_str}

Candidates:
{cands_str}

For each candidate: does it VIOLATE any hard constraint from the Q&A?
ELIMINATE candidates that clearly contradict the evidence.
KEEP candidates that are consistent or ambiguous.

Reply with ONLY valid JSON:
{{"survivors": [0, 2, 3]}}"""


def llm_filter(
    candidates: list[dict],
    enriched_answers: list[dict],
) -> list[dict]:
    """LLM-based elimination using a cheap model. Never returns empty."""
    if len(candidates) <= 3:
        return candidates  # already few enough

    import os
    from gemini_client import generate_json as gemini_json
    model = os.getenv("GEMINI_FILTER_MODEL", "gemini-3.1-flash-lite-preview")

    prompt = _build_filter_prompt(candidates, enriched_answers)
    result = gemini_json(prompt, model=model)
    indices = result.get("survivors", list(range(len(candidates))))

    survivors = [candidates[i] for i in indices if i < len(candidates)]
    return survivors if survivors else candidates
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest q21_improvements/test_deliberation.py -v`
Expected: ALL PASSED

- [ ] **Step 5: Commit**

```bash
git add Q21G-player-whl/candidate_filter.py q21_improvements/test_deliberation.py
git commit -m "feat: LLM elimination filter using Gemini Flash"
```

---

### Task 4: Build two-model council

Independent deliberation by GPT-5.4 and Gemini Pro with confidence-based resolution.

**Files:**
- Create: `Q21G-player-whl/council.py`
- Test: `q21_improvements/test_deliberation.py`

- [ ] **Step 1: Write the failing tests**

Add to `q21_improvements/test_deliberation.py`:

```python
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
    assert resolve_council(gpt, gem) == 0  # GPT tiebreaker
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest q21_improvements/test_deliberation.py -v -k "council"`
Expected: FAIL

- [ ] **Step 3: Implement council.py**

```python
# Area: Player AI - Two-Model Council
# PRD: docs/superpowers/specs/2026-03-23-deliberation-improvements-design.md
"""Two-model deliberation council with confidence-based resolution.

GPT-5.4 and Gemini 3.1 Pro independently evaluate 2-3 candidate
paragraphs. If they disagree, the higher-confidence pick wins.
On tied confidence, GPT wins.
"""
import os

from openai_client import generate_json as gpt_json
from gemini_client import generate_json as gemini_json
from prompts import build_council_prompt


def _call_gpt(prompt: str) -> dict:
    """GPT-5.4 council vote."""
    return gpt_json(prompt)


def _call_gemini(prompt: str) -> dict:
    """Gemini Pro council vote."""
    model = os.getenv("GEMINI_COUNCIL_MODEL", "gemini-2.5-pro-preview-05-06")
    return gemini_json(prompt, model=model)


def resolve_council(gpt_vote: dict, gemini_vote: dict) -> int:
    """Resolve disagreement between two council members.

    Returns the winning candidate index.
    """
    gpt_pick = gpt_vote.get("best_candidate_index", 0)
    gem_pick = gemini_vote.get("best_candidate_index", 0)

    if gpt_pick == gem_pick:
        return gpt_pick

    gpt_conf = gpt_vote.get("confidence", 5)
    gem_conf = gemini_vote.get("confidence", 5)

    if gem_conf > gpt_conf:
        return gem_pick
    return gpt_pick  # GPT wins ties


def council_deliberate(
    candidates: list[dict],
    enriched_answers: list[dict],
) -> dict:
    """Run two-model council on candidates. Returns winning candidate."""
    prompt = build_council_prompt(candidates, enriched_answers)

    gpt_vote = _call_gpt(prompt)
    gemini_vote = _call_gemini(prompt)

    winner_idx = resolve_council(gpt_vote, gemini_vote)
    winner_idx = min(winner_idx, len(candidates) - 1)

    return {
        "best_candidate_index": winner_idx,
        "best_paragraph_text": candidates[winner_idx]["content"],
        "gpt_vote": gpt_vote,
        "gemini_vote": gemini_vote,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest q21_improvements/test_deliberation.py -v -k "council"`
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add Q21G-player-whl/council.py q21_improvements/test_deliberation.py
git commit -m "feat: two-model council with confidence-based resolution"
```

---

### Task 5: Add council prompt and adaptive questions to prompts.py

**Files:**
- Modify: `Q21G-player-whl/prompts.py`

- [ ] **Step 1: Add `build_council_prompt()` to prompts.py**

```python
def build_council_prompt(
    candidates: list[dict], enriched_answers: list[dict],
) -> str:
    """Council deliberation prompt for comparing 2-3 candidates."""
    answers_str = "\n".join(format_answer(a) for a in enriched_answers)
    cands_str = "\n\n---\n\n".join(
        f"Candidate {i}:\n{c['content']}"
        for i, c in enumerate(candidates)
    )
    return f"""You are one member of a deliberation council. Compare these
candidate paragraphs and determine which is the target paragraph.

Evidence from 20 Q&A questions:
{answers_str}

Candidates:
{cands_str}

For each candidate evaluate:
1. Does the FORMAT match the Q&A evidence? (list vs prose vs code)
2. Does the CONTENT match the Q&A evidence? (topic, entities, domain)
3. Does it contain the structural features the answers describe?

Pick the single best match. Score your confidence 1-10 (10 = certain).

Reply with ONLY valid JSON:
{{"best_candidate_index": 0, "confidence": 8, "reasoning": "..."}}"""
```

- [ ] **Step 2: Update `build_questions_prompt()` for adaptive allocation**

Replace the current fixed-block prompt with:

```python
def build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    """Adaptive orthogonal question prompt (20 questions)."""
    return f"""You are playing a 21-questions game. Generate exactly 20
multiple-choice questions to identify a specific opening sentence.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

STEP 1 — ANALYZE THE HINT:
Read the hint carefully. Which dimensions does it already reveal?
- If the hint tells you the DOMAIN → ask fewer domain questions
- If the hint tells you STRUCTURAL features → ask fewer structure questions
- Allocate MORE questions to unknown dimensions

STEP 2 — GENERATE 20 QUESTIONS across these 4 blocks:
(Adjust the count per block based on Step 1. Total MUST be exactly 20.)

FORMATTING & TONE: academic, list, definition, code, etc.
STRUCTURAL: process, comparison, architecture, rule, numbers, thresholds
DOMAIN & ENTITIES: software, cognitive science, protocols, agents, databases
GRANULAR CONTENT: thesis statement, references, figures, metaphors

CRITICAL RULES:
1. Questions must be ORTHOGONAL — each block covers a DIFFERENT dimension.
2. Option D must ALWAYS be: "None of these apply"
3. Options A-C must be specific and concrete, never vague.
4. Focus on narrowing WHICH PARAGRAPH, not which book.

Reply with ONLY valid JSON:
{{"questions": [
  {{"question_number": 1, "question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "None of these apply"}}}},
  ...
]}}"""
```

- [ ] **Step 3: Verify existing tests still pass**

Run: `python -m pytest q21_improvements/test_simulation.py q21_improvements/test_deliberation.py -v`
Expected: ALL PASSED

- [ ] **Step 4: Commit**

```bash
git add Q21G-player-whl/prompts.py
git commit -m "feat: add council prompt and adaptive question allocation"
```

---

### Task 6: Wire everything into my_player.py

Replace the old single-deliberation call with the filter→council pipeline.

**Files:**
- Modify: `Q21G-player-whl/my_player.py`

- [ ] **Step 1: Update imports**

In `my_player.py`, **remove** `build_deliberation_prompt` from the prompts import (it's replaced by the council). **Add** the new imports:

```python
from candidate_filter import deterministic_filter, llm_filter
from council import council_deliberate
```

Remove from existing imports:
```python
# REMOVE this line:
#    build_deliberation_prompt,
```

- [ ] **Step 2: Replace Step 3 (old deliberation) with filter→council**

Replace the current `# ── Step 3: CoT — deliberate on candidates` block (lines 124-133) with:

```python
        # ── Step 3: Hybrid Filter ─────────────────────────────────
        filtered = deterministic_filter(top_candidates, enriched)
        filtered = llm_filter(filtered, enriched)

        if self.logger:
            self.logger.log_phase("phase5_filter", [
                {"content": c["content"][:150] + "..."} for c in filtered
            ])

        # ── Step 4: Two-Model Council ─────────────────────────────
        council_result = council_deliberate(filtered, enriched)

        if self.logger:
            self.logger.log_phase("phase6_council", council_result)

        best_text = council_result.get("best_paragraph_text", candidates_text)
```

And renumber the final guess step to Step 5.

- [ ] **Step 3: Verify the full pipeline compiles**

Run: `python -c "from my_player import MyPlayerAI; print('OK')"`
Expected: `OK` (from Q21G-player-whl directory with CHROMA_PATH=../database)

- [ ] **Step 4: Run all tests**

Run: `python -m pytest q21_improvements/test_simulation.py q21_improvements/test_deliberation.py -v`
Expected: ALL PASSED

- [ ] **Step 5: Commit**

```bash
git add Q21G-player-whl/my_player.py
git commit -m "feat: wire filter→council pipeline into get_guess()"
```

---

### Task 7: Integration test — run real simulation

**Files:**
- Read: `q21_improvements/simulate_player_performance.py`

- [ ] **Step 1: Run stub mode to verify pipeline structure**

```bash
python q21_improvements/simulate_player_performance.py
```

Expected: Completes without errors, prints KPI table.

- [ ] **Step 2: Run real mode**

```bash
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py 2>&1 | tee q21_improvements/council_results.txt
```

Expected: Per-scenario results. Target: ≥3/5 correct paragraph selection.

- [ ] **Step 3: Compare results**

Check `q21_improvements/debug_logs/` for the latest run. Verify:
- `phase5_filter` shows fewer candidates than `phase4_candidates`
- `phase6_council` shows both GPT and Gemini votes
- `final_guess` shows improved sentence matches

- [ ] **Step 4: Commit results**

```bash
git add q21_improvements/council_results.txt
git commit -m "test: council pipeline integration results"
```

- [ ] **Step 5: Push branch**

```bash
git push
```
