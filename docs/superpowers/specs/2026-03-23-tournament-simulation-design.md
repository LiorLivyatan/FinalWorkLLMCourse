# Realistic Tournament Simulation — Design Spec

Version: 1.0.0

## Goal

Generate 10 realistic referee scenarios from the course material PDFs following all official competition rules, run the full player pipeline against them using the real `MyRefereeAI` (LLM-scored), and produce an insight-rich analysis notebook.

## Constraints from Official Rules

| Rule | Source | Implication |
|------|--------|-------------|
| Paragraph from lecture materials | Ch.1 §1.9.1 Phase 1 | Random selection from the 22 indexed PDFs |
| Hint: up to 15 words, NO words from paragraph | Ch.1 §1.9.1 Phase 1.4 | LLM generates + validation script rejects overlaps |
| Association word: player sees topic/category only | Ch.1 §1.9.1 Phase 1.5 | Two fields: `association_word` (shown) and `actual_association_word` (secret) |
| Opening sentence: verbatim quote | Ch.1 §1.9.1 Phase 4.1 | Extracted directly from the chunk, not paraphrased |
| Answers: A, B, C, D, or "not relevant" | Ch.1 §1.9.1 Phase 3 | Already enforced by referee |
| Scoring weights: 50/20/20/10 | Ch.1 Table 10 | Sentence 50%, sent_reason 20%, word 20%, word_reason 10% |
| League points (spec): 85/70/50 | Ch.1 Table 11 | Test alongside SDK thresholds (80/60/40) |

## Architecture

### Component 1: `generate_scenarios.py`

**Randomly generates 10 referee scenarios from the indexed ChromaDB.**

Process per scenario:
1. Query ChromaDB for a random chunk (random offset into the 1490 documents)
2. Extract the first sentence of the chunk as `opening_sentence`
3. Call LLM (Gemini Flash, temp=0) to act as referee and produce:
   - `book_name`: creative title (up to 5 words)
   - `book_hint`: 15-word description with NO words from the paragraph
   - `association_word`: the topic/category shown to players
   - `actual_association_word`: the secret word
   - `warmup_question`: simple math question
4. **Validate**: programmatically check that no word from the hint appears in the paragraph (reject and regenerate if it does)
5. Save all 10 scenarios to `tournament_sim/scenarios_generated.json`

### Component 2: `run_tournament.py`

**Runs MyPlayerAI vs MyRefereeAI for each generated scenario.**

Key design decisions:
- **Uses `MyRefereeAI` from `Q21G-referee-whl/examples/my_ai.py`** — real LLM-scored justifications, real feedback, real answer logic
- **Parameterize `MyRefereeAI`**: modify `__init__` to accept optional `scenario` dict that overrides `book_config` constants. Default behavior (no arg) unchanged for real tournament use.
- **Knowledge base conflict resolution**: both player and referee have their own `knowledge_base.py` module. The tournament runner imports the referee module with a path alias to avoid name collisions. Both point to the same ChromaDB at `./database` (the PyMuPDF-indexed DB). The referee's `ensure_indexed()` must be reordered to check `.indexed` flag **before** `COURSE_MATERIAL_PATH` existence check (same fix as player's — prevents `FileNotFoundError` when pre-built DB exists).
- **Callback context building**: `MyRefereeAI` callbacks expect `ctx: Dict[str, Any]` with `{"dynamic": {...}}` structure. The runner builds proper ctx dicts for each callback, matching the format from `Q21G-referee-whl/src/q21_referee/_gmc/context_builder.py`.
- **Dual scoring**: score each game with BOTH threshold sets:
  - SDK thresholds: 80/60/40
  - Spec thresholds: 85/70/50
- **Error handling**: each game runs independently — if one fails (LLM timeout, rate limit), log the error and continue to the next. Include retry with backoff for Gemini 429 errors.
- **Full game flow per scenario**:
  0. Referee `get_warmup_question(ctx)` → warmup question (skipped for speed, logged as "skipped")
  1. Referee `get_round_start_info(ctx)` → sends book_name, hint, association_word
  2. Player `get_questions(ctx)` → 20 questions
  3. Referee `get_answers(ctx)` → answers via RAG + LLM
  4. Player `get_guess(ctx)` → full pipeline (HyDE → filter → council → extract)
  5. Referee `get_score_feedback(ctx)` → LLM-scored with real justification evaluation
- Saves results + debug logs to `tournament_sim/`

### Component 3: `tournament_analysis.ipynb`

**Jupyter notebook with data tables and LLM-generated narrative insights.**

Sections:
1. **Scenario overview** — table of all 10 scenarios (book name, hint, association word)
2. **Per-scenario results** — sentence score, word match, NR count, league points (both thresholds)
3. **Pipeline diagnostics** — RAG hit rate, filter survival, council agreement
4. **Aggregate KPIs** — avg score, win rate, word accuracy, avg NR
5. **Scoring comparison** — side-by-side: SDK vs spec thresholds impact on league points
6. **LLM Reflector** — GPT-5.4 reads the raw results JSON and produces:
   - Pattern analysis (which scenario types succeed/fail)
   - Failure mode taxonomy (RAG miss vs filter kill vs council misjudge vs extraction error)
   - Actionable recommendations for next improvement iteration

The reflector prompt gives the LLM the role of "Q21 competition strategy advisor" with access to the full results.

## Scenario Schema

Each entry in `scenarios_generated.json`:

```json
{
  "id": 1,
  "source_pdf": "00005.pdf",
  "source_page": 42,
  "book_name": "The Boundary of Cognition",
  "book_hint": "architectural constraint reflecting empirical findings about developer cognitive load thresholds in modular systems",
  "association_word": "limits",
  "actual_association_word": "chunk",
  "opening_sentence": "מגבלת150שורות לקובץ היא לא מספר שרירותי.",
  "full_paragraph": "מגבלת150שורות לקובץ...(full text for referee context)",
  "warmup_question": "What is 12 * 7?"
}
```

## File Structure

```
q21_improvements/
├── generate_scenarios.py          # Random scenario generator
├── run_tournament.py              # Full simulation runner
├── tournament_analysis.ipynb      # Notebook TEMPLATE (tracked in git)
└── tournament_sim/                # ALL OUTPUT (gitignored)
    ├── scenarios_generated.json   # 10 generated scenarios
    ├── results.json               # Full results with dual scoring
    └── debug_logs/                # PhaseLogger output per game
```

## Changes to Existing Files

| File | Change |
|------|--------|
| `Q21G-referee-whl/examples/my_ai.py` | Make `__init__` accept optional `scenario` dict |
| `Q21G-referee-whl/examples/knowledge_base.py` | Fix `ensure_indexed()`: check flag before course path |
| `.gitignore` | Add `q21_improvements/tournament_sim/` |

## Models Used

| Task | Model | Why |
|------|-------|-----|
| Scenario generation | `gemini-3.1-flash-lite-preview` | Cheap, fast — generating hints/words |
| Referee answering | `gemini-3.1-flash-lite-preview` | Same model as real `MyRefereeAI` uses |
| Referee scoring | `gemini-3.1-flash-lite-preview` | Same model as real `MyRefereeAI` uses |
| Player pipeline | GPT-5.4 + Gemini 3.1 Pro | Full council pipeline |
| Notebook reflector | GPT-5.4 | Deep reasoning for insights |
