# Q21G Referee — Implementation Summary

## Overview

Implemented a concrete `MyRefereeAI` subclass for the Q21G League referee package.
The AI uses **Google Gemini** for inference and **Agno RAG + ChromaDB** for accurate question answering,
mirroring the structure of the player package (`Q21G-player-whl`).

**Strategy:** Section 4.3 of the MCP Architecture book, exploiting Miller's Law (7 items in memory = 150-line rule)
to create an asymmetric challenge where the association domain `"memory"` is revealed to players
but the secret scoring word is `"chunk"`.

---

## New Files Created

### `examples/book_config.py`
Game constants for the chosen paragraph. Isolated here so all other modules import a single source of truth.

| Constant | Value |
|---|---|
| `BOOK_NAME` | `"The Non-Arbitrary Line Limit"` |
| `BOOK_HINT` | `"A coding constraint whose precise threshold mirrors psychological research on human attention span boundaries"` |
| `ASSOCIATION_WORD` | `"memory"` ← shown to players |
| `ACTUAL_ASSOCIATION_WORD` | `"chunk"` ← secret scoring target (Miller's Law chunking) |
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
Returns the book name, hint, and `association_word = "memory"` from `book_config`.

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

---

## Detailed Code Logic

### `MyRefereeAI.__init__`

```python
def __init__(self) -> None:
    self._opening_sentence = OPENING_SENTENCE
    self._actual_word = ACTUAL_ASSOCIATION_WORD
    knowledge_base.ensure_indexed()
```

Stores the two secret values the referee needs at runtime — the actual opening sentence and the actual association word — as instance attributes. These are the ground truth used to answer player questions and score player guesses. Calls `ensure_indexed()` immediately so the ChromaDB knowledge base is populated before the first game starts. If the index already exists (flag file present), this is a no-op.

---

### `get_warmup_question`

```python
def get_warmup_question(self, ctx):
    dynamic = ctx.get("dynamic", ctx)
    return {"warmup_question":
            "How many items can the average human hold in short-term memory?"}
```

Returns a fixed warmup question tied to the game strategy. The question references Miller's Law (the answer is ~7), which is the intellectual basis for the 150-line coding rule chosen as the paragraph. This primes sophisticated players to think about the memory/chunking domain before the association word `"memory"` is revealed. The context is unwrapped with `ctx.get("dynamic", ctx)` to handle both the SDK's wrapped format `{"dynamic": {...}}` and raw dict format — a pattern applied consistently across all 4 callbacks.

---

### `get_round_start_info`

```python
def get_round_start_info(self, ctx):
    dynamic = ctx.get("dynamic", ctx)
    return {"book_name": BOOK_NAME, "book_hint": BOOK_HINT,
            "association_word": ASSOCIATION_WORD}
```

Returns the three pieces of information sent to players at the start of a round. All values come from `book_config.py` constants:

- `book_name`: `"The Non-Arbitrary Line Limit"` — an invented title that describes Section 4.3 without giving it away
- `book_hint`: A 13-word description referencing a "psychological research on human attention span boundaries" — points to Miller's Law without naming it
- `association_word`: `"memory"` — a genuine domain/category that naturally contains `"chunk"`. Memory is shown to players as the revealed hint. The secret scoring target is `"chunk"` (which requires reasoning from memory → cognitive psychology → Miller's Law → the chunking mechanism → `"chunk"`)

This asymmetry is the core scoring strategy: weak LLMs will guess words like `"recall"`, `"storage"`, `"cache"` — all plausible memory-domain words but none of them `"chunk"` — and score 0 on the association component. Sophisticated reasoning about working memory capacity leads directly to `"chunk"` and scores 100.

---

### `get_answers`

```python
def get_answers(self, ctx):
    dynamic = ctx.get("dynamic", ctx)
    questions = dynamic.get("questions", [])
    answers = []
    for q in questions:
        answers.append({"question_number": q["question_number"],
                        "answer": self._answer_question(q)})
    return {"answers": answers}
```

Iterates over the player's 20 questions and answers each one individually (sequential, not batched). For each question, delegates to `_answer_question()`. Failures on individual questions never crash the loop — an error on question 5 still produces valid answers for questions 1-4 and 6-20.

#### `_answer_question` (helper)

```python
def _answer_question(self, q):
    context = knowledge_base.search(
        f"150-line limit {q['question_text']}", n_results=2)
    ctx_text = " ".join(r["content"] for r in context)
    opts = q.get("options", {})
    prompt = (
        f'Answer based on this paragraph: "{self._opening_sentence}"\n'
        f'Context: {ctx_text}\n\n'
        f'Question: {q["question_text"]}\n'
        f'A: {opts.get("A","")}  B: {opts.get("B","")}  '
        f'C: {opts.get("C","")}  D: {opts.get("D","")}\n'
        f'Reply only with A, B, C, D, or "Not Relevant".'
    )
    try:
        text = gemini_client.generate(prompt)
        for ch in text:
            if ch in "ABCD":
                return ch
        return "Not Relevant"
    except Exception:
        return "Not Relevant"
```

**Step 1 — RAG retrieval:** Searches the ChromaDB knowledge base with a query combining the fixed anchor `"150-line limit"` and the question text. Returns up to 2 relevant passages from the MCP book chapters to use as context alongside the opening sentence.

**Step 2 — Prompt construction:** Builds a prompt that gives Gemini the actual opening sentence (ground truth), the RAG context passages, the full question text, and all 4 answer options. By anchoring on the real opening sentence, the referee can answer accurately even if Gemini has no prior knowledge of the book.

**Step 3 — Answer extraction:** Scans the response character by character for the first occurrence of `A`, `B`, `C`, or `D`. This is robust against Gemini prepending explanatory text (e.g., "The answer is B because..."). If no valid letter is found or Gemini raises an exception, returns `"Not Relevant"` as the safe fallback.

---

### `get_score_feedback`

```python
def get_score_feedback(self, ctx):
    dynamic = ctx.get("dynamic", ctx)
    guess = dynamic["player_guess"]
    scores = gemini_client.generate_json(self._build_score_prompt(guess))
    if not self._valid_scores(scores):
        scores = self._fallback_scores(guess)
    return self._build_response(scores)
```

Orchestrates scoring in three stages: build prompt → call Gemini → validate → fallback if needed → build response. The `player_guess` field is a nested `PlayerGuess` TypedDict inside the dynamic context (not a flat field), so it is accessed as `dynamic["player_guess"]`.

#### `_build_score_prompt` (helper)

Constructs an explicit multi-line prompt showing Gemini both the actual values (from instance state) and the player's guessed values side by side. Uses `<int 0-100>` placeholder syntax and the instruction `"Return ONLY valid JSON with exactly these keys"` to minimise the chance of the model returning schema strings literally or wrapping output in markdown. Requests 150-200 words per feedback field to meet the SDK's `FeedbackMessages` requirement.

#### `_valid_scores` (helper)

```python
def _valid_scores(self, s):
    required = ["opening_sentence_score", "sentence_justification_score",
                "associative_word_score", "word_justification_score",
                "opening_sentence_feedback", "associative_word_feedback"]
    return all(k in s for k in required)
```

Checks that the parsed JSON contains all 6 required keys. Any missing key (e.g. Gemini returned a partial response or an empty dict `{}`) triggers the fallback path.

#### `_fallback_scores` (helper)

```python
def _fallback_scores(self, guess):
    sent = difflib.SequenceMatcher(
        None, norm(self._opening_sentence),
        norm(guess.get("opening_sentence", ""))).ratio() * 100
    word = 100.0 if norm(self._actual_word) == norm(
        guess.get("associative_word", "")) else 0.0
    ...
```

Used only when Gemini fails to return valid JSON. Scores the two most important components deterministically:

- **Opening sentence score**: `difflib.SequenceMatcher` ratio (0.0–1.0) × 100, comparing normalised (lowercase, stripped) actual vs guessed sentence. This gives a meaningful similarity score without needing an LLM.
- **Association word score**: Exact match only — 100 if the normalised guessed word equals `"chunk"`, 0 otherwise.
- **Justification scores**: Both set to 0.0 since there is no LLM available to evaluate reasoning quality.
- **Feedback strings**: 150-200 word fallback templates from `book_config.py` explaining the scoring methodology, meeting the SDK requirement even in the fallback path.

#### `_build_response` (helper)

```python
def _build_response(self, s):
    private = (s["opening_sentence_score"] * 0.5
               + s["sentence_justification_score"] * 0.2
               + s["associative_word_score"] * 0.2
               + s["word_justification_score"] * 0.1)
    return {
        "league_points": self._score_to_league_points(private),
        "private_score": round(private, 2),
        "breakdown": {...},
        "feedback": {...},
    }
```

Applies the official weighted formula to compute `private_score` (0–100), then converts to `league_points` (0–3) using the SDK thresholds. Reshapes the flat scores dict into the nested `ScoreFeedbackResponse` structure the SDK expects: scores go into `breakdown`, feedback strings go into `feedback`.

#### `_score_to_league_points` (helper)

```python
@staticmethod
def _score_to_league_points(score):
    if score >= 80: return 3
    if score >= 60: return 2
    if score >= 40: return 1
    return 0
```

Converts the continuous private score to the discrete league points value. Thresholds (80/60/40) match the SDK's `ScoreFeedbackResponse` docstring exactly, which takes precedence over the book's different thresholds (85/70/50).

---

### RAG Knowledge Base (`knowledge_base.py`)

```
ensure_indexed() → get_knowledge() → _build_knowledge()
search(query, n_results) → get_knowledge() → kb.search()
```

**`_build_knowledge()`** — Constructs an Agno `Knowledge` object backed by a local persistent `ChromaDb` instance. Uses `GeminiEmbedder` with `vertexai=False` so it authenticates via `GOOGLE_API_KEY` (not Vertex AI credentials). Collection name is `"mcp_book"`. ChromaDB path is configurable via `CHROMA_PATH` env var (default `tmp/chromadb`).

**`get_knowledge()`** — Lazy singleton: builds the `Knowledge` object once on first call and caches it in the module-level `_knowledge` variable. Subsequent calls return the cached instance.

**`ensure_indexed()`** — Idempotent indexing: checks for a `.indexed` flag file inside the ChromaDB path. If missing, calls `kb.insert(path=...)` to embed and store all markdown chapters from `COURSE_MATERIAL_PATH`. Creates the flag file on completion. If the course material directory doesn't exist (e.g. not yet downloaded), silently returns — this makes the referee start cleanly in any environment.

**`search(query, n_results)`** — Calls `kb.search()` and maps results to `[{"content": str}]` dicts. Wraps everything in a try/except so any ChromaDB or embedder error returns `[]` instead of crashing the referee mid-game.

---

### Gemini Client (`gemini_client.py`)

**`generate(prompt)`** — Sends a plain text prompt to the Gemini API and returns the response text. Model is read from the `GEMINI_MODEL` env var, defaulting to `gemini-3.1-flash-lite-preview`. The `_client` is instantiated once at module import time (eager init) using `GOOGLE_API_KEY`.

**`generate_json(prompt)`** — Wraps `generate()` and passes the result to `_parse_json()`.

**`_parse_json(text)`** — First tries to strip a markdown code fence (` ```json ... ``` ` or ` ``` ... ``` `) using a regex. Then attempts `json.loads()` on the cleaned text. Returns `{}` on any parse failure, so callers always get a dict and never a raw exception.

---

### Strategic Design Summary

The implementation is built around one core idea: **choose a paragraph that is easy for the referee to answer accurately but hard for weak LLMs to guess**.

Section 4.3 satisfies this because:
1. The opening sentence is a concrete, unambiguous claim about a specific number
2. The hint points to cognitive psychology research without naming it
3. The revealed association word `"memory"` is a genuine domain/category for `"chunk"` — making the pair fair and defensible under the rules
4. The secret word `"chunk"` requires a chain of reasoning: memory → cognitive psychology → Miller's Law → the chunking mechanism
5. Weak LLMs playing as the player will guess words like `"recall"`, `"storage"`, `"cache"`, or `"retention"` — all plausible memory-domain words but none of them `"chunk"` — scoring 0 on the association component (20% of total score)
