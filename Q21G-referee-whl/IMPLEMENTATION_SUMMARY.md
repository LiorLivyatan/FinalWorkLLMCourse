# Q21G Referee — Implementation Summary

## Overview

Implemented a concrete `MyRefereeAI` subclass for the Q21G League referee package.
The AI uses **Google Gemini** for inference and **Agno RAG + ChromaDB** for accurate question answering,
mirroring the structure of the player package (`Q21G-player-whl`).

**Strategy:** Section 4.3 of the MCP Architecture book, exploiting Miller's Law (7 items in memory = 150-line rule)
to create an asymmetric challenge where the association domain `"cognition"` is revealed to players
but the secret scoring word is `"seven"`.

---

## New Files Created

### `examples/book_config.py`
Game constants for the chosen paragraph. Isolated here so all other modules import a single source of truth.

| Constant | Value |
|---|---|
| `BOOK_NAME` | `"The Non-Arbitrary Line Limit"` |
| `BOOK_HINT` | `"A coding constraint whose precise threshold mirrors psychological research on human attention span boundaries"` |
| `ASSOCIATION_WORD` | `"cognition"` ← shown to players |
| `ACTUAL_ASSOCIATION_WORD` | `"seven"` ← secret scoring target (Miller's Law) |
| `OPENING_SENTENCE` | `"The 150-line limit per file is not an arbitrary number."` |

---

### `examples/gemini_client.py`
Thin wrapper around `google-genai` SDK. Mirrors the player package pattern exactly.

- `generate(prompt)` — returns raw text from Gemini
- `generate_json(prompt)` — parses JSON from response, strips markdown code fences, returns `{}` on failure
- Reads `GOOGLE_API_KEY` from environment (not `GEMINI_API_KEY`)
- Default model: `gemini-3.1-flash-lite-preview` (overridable via `GEMINI_MODEL` env var)
- Module-level `_client` instantiated eagerly at import time

---

### `examples/knowledge_base.py`
Agno RAG knowledge base over the MCP Architecture book English chapters.

- Uses `agno.knowledge.knowledge.Knowledge` + `ChromaDb` (local persistent) + `GeminiEmbedder`
- Collection name: `mcp_book`
- `ensure_indexed()` — indexes chapters once, marks completion with `.indexed` flag file; silently skips if `COURSE_MATERIAL_PATH` directory does not exist
- `search(query, n_results)` — returns `list[{"content": str}]`, returns `[]` on any error
- `vertexai=False` — uses `GOOGLE_API_KEY` (not Vertex AI credentials)

Environment variables:
| Variable | Default | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | (required) | Gemini API + embeddings |
| `CHROMA_PATH` | `tmp/chromadb` | ChromaDB storage path |
| `COURSE_MATERIAL_PATH` | `../chapters_en` | Path to English chapter markdown files |

---

### `examples/my_ai.py` (145 lines)
The main student implementation — `MyRefereeAI(RefereeAI)`.

#### Callback 1: `get_warmup_question`
Returns a fixed warmup question tied to the strategy:
> *"How many items can the average human hold in short-term memory?"*

Primes players to think about Miller's Law before revealing the association word.

#### Callback 2: `get_round_start_info`
Returns the book name, hint, and `association_word = "cognition"` from `book_config`.

#### Callback 3: `get_answers`
Answers each of the player's 20 questions **sequentially** (one Gemini call per question):
1. RAG search on `knowledge_base` for relevant context snippets
2. Sends question + options + paragraph + context to Gemini
3. Extracts first `A/B/C/D` character from response; falls back to `"Not Relevant"` on failure or API error
4. Never crashes — exceptions per-question are caught and isolated

#### Callback 4: `get_score_feedback`
Scores the player's guess using Gemini, with a `difflib` fallback:
- Calls `generate_json()` with a structured prompt comparing player guess to actual values
- If Gemini returns invalid/incomplete JSON → fallback to string similarity (`difflib.SequenceMatcher`) for sentence score and exact match for word score
- Applies official scoring formula:
  ```
  private_score = sentence_score×0.5 + sentence_justification×0.2
                + word_score×0.2 + word_justification×0.1
  ```
- Converts to `league_points`: 3 (≥80), 2 (≥60), 1 (≥40), 0 (otherwise)

**Score prompt** — explicit multi-line format with `<int 0-100>` placeholders and `"Return ONLY valid JSON with exactly these keys"` to prevent the model from returning literal schema strings.

**Context unwrap pattern** — all 4 callbacks assign the result in all cases:
```python
dynamic = ctx.get("dynamic", ctx)
```

---

### `tests/test_book_config.py` (4 tests)
| Test | What it checks |
|---|---|
| `test_all_constants_non_empty` | All 5 constants are non-empty strings |
| `test_hint_within_15_words` | `BOOK_HINT` ≤ 15 words |
| `test_association_word_differs_from_actual` | Public word ≠ secret word |
| `test_opening_sentence_ends_with_period` | Sentence ends with `.` |

---

### `tests/test_gemini_client.py` (4 tests)
| Test | What it checks |
|---|---|
| `test_generate_calls_gemini` | `generate()` calls `models.generate_content` and returns text |
| `test_generate_json_parses_valid_json` | `generate_json()` parses clean JSON string |
| `test_generate_json_handles_code_fence` | Strips ` ```json ... ``` ` markdown wrapper |
| `test_generate_json_returns_empty_on_bad_json` | Returns `{}` when response is not valid JSON |

---

### `tests/test_knowledge_base.py` (3 tests)
| Test | What it checks |
|---|---|
| `test_search_returns_list_of_dicts` | `search()` returns `[{"content": str}]` |
| `test_search_returns_empty_list_on_error` | Returns `[]` when KB raises an exception |
| `test_ensure_indexed_skips_missing_path` | `ensure_indexed()` does not call `insert()` if directory missing |

---

### `tests/test_my_ai.py` (18 tests)
| Test | What it checks |
|---|---|
| `test_warmup_returns_question` | Returns dict with non-empty `warmup_question` |
| `test_warmup_wrapped_and_raw` | Same result for wrapped and raw context |
| `test_round_start_returns_book_info` | Returns correct `book_name`, `book_hint`, `association_word` |
| `test_round_start_wrapped_and_raw` | Same result for wrapped and raw context |
| `test_answers_happy_path` | Returns 3 answers, each is a valid choice |
| `test_answers_partial_failure_continues` | API error on Q2 → `"Not Relevant"`, Q1/Q3 succeed |
| `test_answers_all_gibberish_returns_not_relevant` | All gibberish responses → all answers `"Not Relevant"` |
| `test_answers_wrapped_and_raw` | Same answer count for wrapped and raw context |
| `test_score_happy_path` | Returns `league_points`, `private_score`, `breakdown`, `feedback` |
| `test_score_llm_failure_uses_fallback` | Empty LLM response triggers `difflib` fallback |
| `test_score_wrapped_and_raw` | Same `league_points` for wrapped and raw context |
| `test_score_none_actuals_use_instance_state` | `actual_opening_sentence`/`actual_associative_word` = None → no crash, instance state used |
| `test_league_points_boundaries` (×6) | Boundary values: 80→3, 79.9→2, 60→2, 59.9→1, 40→1, 39.9→0 |

---

### `docs/superpowers/specs/2026-03-20-student-referee-ai-design.md`
Design spec (v1.4.0) — strategy rationale, architecture decisions, scoring formula, context unwrap pattern.
Passed 4 spec review iterations.

### `docs/superpowers/plans/2026-03-20-student-referee-ai.md`
TDD implementation plan — task-by-task breakdown with file paths, code samples, and test commands.
Updated to reflect Agno/player pattern with `examples/` layout.

---

## Pre-Existing Files Modified

### `pyproject.toml`
Added dependencies to the `llm` optional group:
```toml
[project.optional-dependencies]
llm = [
    "anthropic>=0.18.0",
    "google-genai>=1.0.0",   # ← added
    "agno>=2.4.0",            # ← added
    "chromadb>=0.5.0",        # ← added
    "pypdf>=4.0.0",           # ← added
]
```

### `.env.template`
Added three new environment variable entries:
```
GOOGLE_API_KEY=your_google_api_key_here
COURSE_MATERIAL_PATH=../chapters_en
CHROMA_PATH=./tmp/chromadb
```

### `tests/conftest.py`
Added session-scope setup required for the new `examples/` modules:
- Inserts `examples/` onto `sys.path` so all test files can import student modules
- Sets `GOOGLE_API_KEY=fake-key-for-tests` before any import
- Patches `google.genai.Client` at session scope to prevent `ValueError` from eager module-level init in `gemini_client.py`
- Provides shared test fixtures used by `test_my_ai.py`:
  - `VALID_SCORES` — a complete valid score response dict
  - `make_warmup_ctx()` — warmup context (wrapped or raw)
  - `make_round_ctx()` — round start context with two players
  - `make_questions(n)` — list of N question dicts
  - `make_answers_ctx()` — answers context with questions
  - `make_score_ctx()` — score feedback context with player guess

---

## Test Results

All 29 new tests pass:
```
tests/test_my_ai.py          18 passed
tests/test_book_config.py     4 passed
tests/test_gemini_client.py   4 passed
tests/test_knowledge_base.py  3 passed
──────────────────────────────────────
29 passed in 0.94s
```

Run with:
```bash
uv pip install -e "."          # install package (once per environment)
uv run pytest tests/ -v
```
