# Student RefereeAI Implementation Design

Version: 1.4.0

## Overview

Implement a concrete `StudentRefereeAI` subclass of `RefereeAI` (from `callbacks.py`)
for the Q21G League. Uses Google Gemini (`gemini-3.1-flash-lite-preview`) for answering
player questions and scoring guesses. Book content is fixed to Section 4.3 of the MCP
Architecture book — chosen to maximize referee league score via strategic hint design.

---

## Strategic Context

- The external League Manager awards the referee **2 pts** for a decisive result (one player
  wins), **0 pts** for a draw or failure. This is an external scoring mechanism — it is NOT
  part of `ScoreFeedbackResponse`. `ScoreFeedbackResponse.league_points` (0-3) is the
  *player's* league score, not the referee's.
- Optimal strategy: moderately difficult hint creating asymmetric player outcomes.
- Chosen paragraph: §4.3 opening sentence — *"The 150-line limit per file is not an arbitrary number."*
- Association word domain: `"memory"` (shown to players — a genuine category that contains "chunk").
- Secret association word: `"chunk"` (Miller's Law — working memory operates via chunking; the 150-line rule is calibrated to one cognitive chunk).
- Strong players who reason: memory → cognitive psychology → Miller's Law → chunking mechanism → will guess "chunk" correctly.

---

## File Structure

```
src/q21_referee/
├── student_ai.py       # StudentRefereeAI class (4 callbacks)
├── gemini_client.py    # Gemini API wrapper
└── book_config.py      # Hardcoded book constants

tests/
├── test_student_ai.py
├── test_gemini_client.py
└── test_book_config.py
```

All files must stay under 150 lines (CLAUDE.md rule).
Each file must have `# Area: Student Callbacks` and `# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md` header comments.

---

## Book Constants (`book_config.py`)

```python
# These are game design constants chosen by the referee's strategic game setup.
# ACTUAL_ASSOCIATION_WORD is intentionally hardcoded as it is the referee's
# fixed strategic choice, not a runtime secret or credential.
BOOK_NAME = "The Non-Arbitrary Line Limit"
BOOK_HINT = "A coding constraint whose precise threshold mirrors psychological research on human attention span boundaries"
ASSOCIATION_WORD = "memory"             # domain shown to players
ACTUAL_ASSOCIATION_WORD = "chunk"       # secret word players must guess
OPENING_SENTENCE = "The 150-line limit per file is not an arbitrary number."
```

Gemini API key comes from environment variable `GEMINI_API_KEY` (never hardcoded).

---

## `gemini_client.py`

- Module-level singleton: `_client = None` initialized once via `_get_client()`.
- `_get_client()` reads `GEMINI_API_KEY` from `os.environ`; raises `RuntimeError` if missing.
- Instantiates `google.genai.Client(api_key=key)` once and caches it.
- Single public function: `ask(prompt: str) -> str`
  - Calls `_get_client().models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)`
  - Returns `response.text.strip()`
  - Re-raises any API exception as `RuntimeError`

---

## `student_ai.py` — `StudentRefereeAI`

### Secret State (set in `__init__`)

```python
self._opening_sentence = OPENING_SENTENCE
self._actual_word = ACTUAL_ASSOCIATION_WORD
```

### Callback 1 — `get_warmup_question`

- Context unwrap: `dynamic = ctx.get("dynamic", ctx)` (required even if not used).
- No LLM call. Returns hardcoded question:
  `"How many items can the average human hold in short-term memory?"`
- Deadline: 30s. Zero risk.

### Callback 2 — `get_round_start_info`

- Context unwrap: `dynamic = ctx.get("dynamic", ctx)`
- Player access (matching `types.py`): `dynamic["player_a"]`, `dynamic["player_b"]`.
  **WARNING**: The docstring example in `callbacks.py` uses `player1`/`player2` — these
  field names are WRONG. The authoritative field names from `types.py` are `player_a` and
  `player_b`. Do not follow the docstring example.
- No LLM call. Returns hardcoded constants from `book_config.py`.
- Returns: `{book_name, book_hint, association_word}`
- Deadline: 60s. Zero risk.

### Callback 3 — `get_answers`

- Context unwrap: `dynamic = ctx.get("dynamic", ctx)`
- Iterates `dynamic["questions"]` **sequentially** (one Gemini call per question).
- Each question call is wrapped in `try/except`; on any exception (including `RuntimeError`
  from missing API key), falls back to `"Not Relevant"` for that question and **continues**
  with remaining questions.
- Per-question prompt:
  ```
  You are answering questions about this paragraph:
  "{OPENING_SENTENCE}"

  Question: {question_text}
  A: {options[A]}
  B: {options[B]}
  C: {options[C]}
  D: {options[D]}

  Answer only with A, B, C, D, or "Not Relevant".
  ```
- Parse response: extract first A/B/C/D character; fallback to `"Not Relevant"` on parse failure.
- Returns: `{"answers": [{question_number, answer}, ...]}`
- Deadline: 120s for 20 calls (~6s/call budget).

### Callback 4 — `get_score_feedback`

- Context unwrap: `dynamic = ctx.get("dynamic", ctx)`
- Player guess access: `guess = dynamic["player_guess"]` (nested `PlayerGuess` TypedDict).
  Fields: `guess["opening_sentence"]`, `guess["sentence_justification"]`,
  `guess["associative_word"]`, `guess["word_justification"]`.
- Truth values for scoring (always use instance state — both are guaranteed by `__init__`):
  - Sentence truth: `self._opening_sentence`
  - Word truth: `self._actual_word`
  - Do NOT use `actual_opening_sentence` or `actual_associative_word` from the context —
    they are `Optional[str]` and may be `None`.
  - Note: `dynamic["association_word"]` is the referee's own domain word ("memory"),
    NOT the secret word and NOT the player's guess. The player's guess is in
    `dynamic["player_guess"]["associative_word"]`.
- Single Gemini call requesting JSON scores (0-100 each).
- Gemini prompt template:
  ```
  You are scoring a player's guess about a paragraph.

  ACTUAL opening sentence: "{actual_sentence}"
  PLAYER guessed opening sentence: "{sentence_guess}"
  Player's justification for sentence: "{sentence_just}"

  ACTUAL association word: "{actual_word}"
  PLAYER guessed association word: "{word_guess}"
  Player's justification for word: "{word_just}"

  Score each component 0-100 and provide feedback (2-3 sentences each).
  Return ONLY valid JSON with exactly these keys:
  {{
    "opening_sentence_score": <float 0-100>,
    "sentence_justification_score": <float 0-100>,
    "associative_word_score": <float 0-100>,
    "word_justification_score": <float 0-100>,
    "opening_sentence_feedback": "<2-3 sentence feedback>",
    "associative_word_feedback": "<2-3 sentence feedback>"
  }}
  ```
- JSON extraction: strip markdown code fences before parsing.
  Pattern: `re.sub(r'```(?:json)?\s*|\s*```', '', response_text).strip()`, then `json.loads()`.
- Gemini prompt requests flat JSON:
  ```json
  {
    "opening_sentence_score": float,
    "sentence_justification_score": float,
    "associative_word_score": float,
    "word_justification_score": float,
    "opening_sentence_feedback": str,
    "associative_word_feedback": str
  }
  ```
- **Response reshaping** (required before returning):
  ```python
  breakdown = {
      "opening_sentence_score": ...,
      "sentence_justification_score": ...,
      "associative_word_score": ...,
      "word_justification_score": ...,
  }
  feedback = {
      "opening_sentence": gemini_json["opening_sentence_feedback"],
      "associative_word": gemini_json["associative_word_feedback"],
  }
  ```
- Private score formula (use exact key names from `ScoreBreakdown`):
  `opening_sentence_score*0.5 + sentence_justification_score*0.2 + associative_word_score*0.2 + word_justification_score*0.1`
- League points: `3 if >=80, 2 if >=60, 1 if >=40, else 0` (per `types.py` docstring).
- **Fallback** if JSON parse fails:
  - `opening_sentence_score`: `difflib.SequenceMatcher(None, norm(actual), norm(guess)).ratio() * 100`
    where `norm(s) = s.lower().strip()`
  - `associative_word_score`: `100.0` if `norm(actual_word) == norm(guess_word)` else `0.0`
  - `sentence_justification_score`: `0.0` (cannot assess without LLM)
  - `word_justification_score`: `0.0` (cannot assess without LLM)
  - `feedback.opening_sentence`: `"Score computed via string similarity (LLM unavailable)."`
  - `feedback.associative_word`: `"Score computed via exact match (LLM unavailable)."`
- Deadline: 180s. Low risk.

---

## Error Handling

| Callback | LLM Failure Fallback |
|---|---|
| `get_answers` | Catch `Exception` per-question; return `"Not Relevant"`, continue remaining questions |
| `get_score_feedback` | Catch `Exception` on Gemini call or JSON parse; use difflib + exact match |

---

## TDD Plan

Test files mirror each module. Write tests **before** implementation.

### `test_book_config.py`
- All 5 constants present and non-empty strings
- `ASSOCIATION_WORD != ACTUAL_ASSOCIATION_WORD`

### `test_gemini_client.py`
- Missing `GEMINI_API_KEY` raises `RuntimeError`
- Successful call returns stripped text (mock `google.genai.Client`)
- API exception is re-raised as `RuntimeError`

### `test_student_ai.py`
- **Callback 1**: returns dict with `warmup_question` key; ctx unwrap works with both wrapped and raw ctx
- **Callback 2**: returns `book_name`, `book_hint`, `association_word`; uses `player_a`/`player_b` keys; ctx unwrap works with both wrapped and raw ctx
- **Callback 2 — wrong keys**: passing ctx with `player1`/`player2` does NOT break (keys unused, no KeyError)
- **Callback 3 — happy path**: mock `ask()` returns `"B"`; all 20 answers are `"B"`; ctx unwrap works with both wrapped and raw ctx
- **Callback 3 — partial failure**: mock `ask()` raises on question 5; questions 1-4 have answers, question 5 is `"Not Relevant"`, questions 6-20 continue
- **Callback 3 — parse failure**: mock `ask()` returns gibberish; all answers are `"Not Relevant"`
- **Callback 4 — happy path**: mock `ask()` returns valid JSON; scores, breakdown, feedback, league_points correct; ctx unwrap works with both wrapped and raw ctx
- **Callback 4 — JSON parse failure**: falls back to difflib; returns valid `ScoreFeedbackResponse`
- **Callback 4 — `actual_opening_sentence` is None**: instance state used; no crash
- **Callback 4 — `actual_associative_word` is None**: instance state used; no crash
- **League points boundaries**: private_score=80.0→3, 79.9→2, 60.0→2, 59.9→1, 40.0→1, 39.9→0

---

## Constraints Checklist

- [x] All files < 150 lines
- [x] TDD: tests written before implementation
- [x] `# Area: Student Callbacks` / `# PRD: docs/superpowers/specs/...` headers in all files
- [x] No hardcoded API keys (env var `GEMINI_API_KEY`); game constants justified in comment
- [x] Context unwrap via `ctx.get("dynamic", ctx)` in **all 4** callbacks (including callback 1)
- [x] `league_points` thresholds: 3≥80, 2≥60, 1≥40, else 0
- [x] `player_guess` accessed as nested dict: `dynamic["player_guess"]["opening_sentence"]`
- [x] Player fields use `player_a`/`player_b` (matching `types.py`), not `player1`/`player2`
- [x] Sequential Gemini calls for `get_answers` with per-question exception handling
- [x] Gemini response reshaped to nested `breakdown`/`feedback` dicts before returning
- [x] Module-level Gemini client singleton (avoid re-instantiation per call)
- [x] `StudentRefereeAI` is NOT exported from `src/q21_referee/__init__.py` (that file is
  proprietary — no modifications permitted). Import directly:
  `from q21_referee.student_ai import StudentRefereeAI`
