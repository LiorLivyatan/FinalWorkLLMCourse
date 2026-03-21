# Q21 Evaluation Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fast, deterministic, offline evaluation harness that measures MyPlayerAI performance against ground-truth scenarios before applying improvements (HyDE RAG, orthogonal questions, CoT deliberation).

**Architecture:** A `MockReferee` answers player questions via keyword-matching (no LLM) and scores guesses with string similarity. Ground-truth scenarios define the book/sentence/word for each game. A runner script loops over scenarios, calls MyPlayerAI callbacks directly, and reports 3 KPIs: win rate, word accuracy, and information density (Not Relevant count).

**Tech Stack:** Python 3.12, difflib (scoring), pytest (tests), dotenv (env loading), ChromaDB + Gemini (player side only, via MyPlayerAI)

---

## File Structure

```
q21_improvements/
├── __init__.py                        # Package marker (empty)
├── scenarios.py                       # 3 ground-truth scenario dicts
├── mock_referee.py                    # MockReferee class (no LLM)
├── simulate_player_performance.py     # Main runner + reporting
├── test_simulation.py                 # 16 TDD tests
└── improvement_plan.md                # Original improvement plan (reference)
```

## Status: Tasks 2-4 DONE, Tasks 1, 5-6 REMAINING

Tasks 2-4 are already implemented and passing (16/16 tests, stub mode verified). Tasks 1, 5, and 6 are the remaining work. The spec calls for 10 scenarios; we start with 3 representative ones (our referee's paragraph, a harder multi-agent one, a contrasting infrastructure one) and can expand later.

---

### Task 1: Create package marker — REMAINING

**Files:**
- Create: `q21_improvements/__init__.py`

- [ ] **Step 1: Create empty __init__.py**

```python
# q21_improvements package
```

- [ ] **Step 2: Verify imports still work**

Run: `python -m pytest q21_improvements/test_simulation.py -v`
Expected: 16 passed

- [ ] **Step 3: Commit**

```bash
git add q21_improvements/__init__.py
git commit -m "feat: add q21_improvements package marker"
```

---

### Task 2: Ground-truth scenarios ✅ DONE

**Files:**
- `q21_improvements/scenarios.py` (60 lines)

Already implemented with 3 scenarios:
- Scenario 1: The Non-Arbitrary Line Limit (our referee's paragraph) — `association_word="memory"`, `actual_association_word="chunk"`, `opening_sentence="The 150-line limit per file is not an arbitrary number."`
- Scenario 2: System Design Principles (Ch. 3) — harder, generic opening
- Scenario 3: Gmail as Agent Transport (Ch. 4) — contrasting infrastructure domain

---

### Task 3: MockReferee ✅ DONE

**Files:**
- `q21_improvements/mock_referee.py` (92 lines)

Already implemented:
- `get_round_start_info()` — returns public book fields
- `answer_questions()` — keyword-matches options against sentence + hint, falls back to "Not Relevant"
- `score_guess()` — `difflib.SequenceMatcher` for sentence, exact match for word, weights 50/20/20/10
- `_score_to_league_points()` — thresholds 90/80/60

---

### Task 4: Tests ✅ DONE

**Files:**
- `q21_improvements/test_simulation.py` (121 lines)

16 tests covering:
- `answer_questions()`: sentence match, hint match, Not Relevant fallback, question number preservation
- `score_guess()`: exact match, wrong word, partial sentence, empty guess
- `_score_to_league_points()`: all 4 boundary values (90, 80, 60, <60)
- Scenario integrity: exact sentence, word separation, count, required fields

---

### Task 5: Run real player baseline ✅ REMAINING

**Files:**
- Read: `q21_improvements/simulate_player_performance.py`
- Read: `.env` (must have GOOGLE_API_KEY set)

This task requires API keys. Run when environment is configured.

- [ ] **Step 1: Verify .env has required keys**

Run: `python -c "from dotenv import load_dotenv, find_dotenv; load_dotenv(find_dotenv(usecwd=True)); import os; print('KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'MISSING')"`
Expected: `KEY: SET`

- [ ] **Step 2: Run simulation with real MyPlayerAI**

Run: `SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py`
Expected: Colored output showing per-scenario scores and aggregate KPIs. This is the pre-improvement baseline.

- [ ] **Step 3: Save baseline results**

Copy the terminal output to `q21_improvements/baseline_results.txt` for later comparison after applying HyDE/orthogonal improvements.

```bash
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py 2>&1 | tee q21_improvements/baseline_results.txt
```

- [ ] **Step 4: Commit baseline**

```bash
git add q21_improvements/baseline_results.txt
git commit -m "docs: save pre-improvement baseline KPI results"
```

---

### Task 6: Add JSON export for iteration tracking ✅ REMAINING

**Files:**
- Modify: `q21_improvements/simulate_player_performance.py`

Add JSON output so results can be compared across improvement iterations programmatically.

- [ ] **Step 1: Write the failing test**

Add to `q21_improvements/test_simulation.py`:

```python
def test_run_game_returns_required_keys():
    """Verify run_game returns all KPI-relevant fields."""
    from q21_improvements.simulate_player_performance import run_game
    from q21_improvements.scenarios import SCENARIO_1
    result = run_game(SCENARIO_1)
    required = {"name", "guessed", "actual", "word_guessed", "word_actual",
                "nr", "opening_sentence_score", "word_score", "private_score",
                "league_points"}
    assert required.issubset(result.keys())
```

- [ ] **Step 2: Run test to verify it passes (already works)**

Run: `python -m pytest q21_improvements/test_simulation.py::test_run_game_returns_required_keys -v`
Expected: PASS (the interface is already correct)

- [ ] **Step 3: Add JSON export to main block**

Add at the end of `simulate_player_performance.py`, inside `if __name__ == "__main__":`:

```python
    import json
    out = "q21_improvements/eval_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  {C.DIM}Results saved to {out}{C.RESET}")
```

- [ ] **Step 4: Run simulation and verify JSON output**

Run: `python q21_improvements/simulate_player_performance.py`
Then: `python -c "import json; d=json.load(open('q21_improvements/eval_results.json')); print(len(d), 'scenarios')"`
Expected: `3 scenarios`

- [ ] **Step 5: Verify all tests still pass**

Run: `python -m pytest q21_improvements/test_simulation.py -v`
Expected: 17 passed

- [ ] **Step 6: Commit**

```bash
git add q21_improvements/simulate_player_performance.py q21_improvements/test_simulation.py
git commit -m "feat: add JSON export to eval pipeline for iteration tracking"
```

---

## Post-Completion: Next Improvements

After this pipeline is in place and baseline is captured, the improvement plan has 3 more tasks:

1. **Task 2: HyDE RAG** — Use referee answers to synthesize a hypothetical paragraph for better retrieval
2. **Task 3: Orthogonal Questions** — Non-overlapping question blocks (Formatting, Temporal, Domains, Structure)
3. **Task 4: Agentic CoT** — Multi-step reasoning for the final guess

Each improvement should be followed by re-running `SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py` and comparing against the baseline JSON.
