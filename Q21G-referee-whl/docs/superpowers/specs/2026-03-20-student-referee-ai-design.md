# Student RefereeAI Implementation Design

Version: 1.0.0

## Overview

Implement a concrete `StudentRefereeAI` subclass of `RefereeAI` (from `callbacks.py`)
for the Q21G League. Uses Google Gemini (`gemini-3.1-flash-lite-preview`) for answering
player questions and scoring guesses. Book content is fixed to Section 4.3 of the MCP
Architecture book — chosen to maximize referee league score via strategic hint design.

---

## Strategic Context

- Referee earns **2 pts** for decisive result (one player wins), **0 pts** for draw or failure.
- Optimal strategy: moderately difficult hint creating asymmetric player outcomes.
- Chosen paragraph: §4.3 opening sentence — *"The 150-line limit per file is not an arbitrary number."*
- Association word domain: `"cognition"` (shown to players).
- Secret association word: `"seven"` (Miller's Law — the cognitive science basis for the 150-line rule).
- Strong players who reason: cognition + code quality + why-150 → Miller's 7 items → will guess correctly.

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
Each file must have `# Area:` and `# PRD:` header comments.

---

## Book Constants (`book_config.py`)

```python
BOOK_NAME = "The Non-Arbitrary Line Limit"
BOOK_HINT = "A coding constraint whose precise threshold mirrors psychological research on human attention span boundaries"
ASSOCIATION_WORD = "cognition"          # domain shown to players
ACTUAL_ASSOCIATION_WORD = "seven"       # secret word players must guess
OPENING_SENTENCE = "The 150-line limit per file is not an arbitrary number."
```

These are game design constants, not credentials — hardcoded is acceptable.
Gemini API key comes from environment variable `GEMINI_API_KEY`.

---

## `gemini_client.py`

Single function: `ask(prompt: str) -> str`

- Loads `GEMINI_API_KEY` from `os.environ`
- Calls `google.genai.Client().models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)`
- Returns `response.text.strip()`
- Raises `RuntimeError` if key missing or API call fails

---

## `student_ai.py` — `StudentRefereeAI`

### Secret State (set in `__init__`)

```python
self._opening_sentence = OPENING_SENTENCE
self._actual_word = ACTUAL_ASSOCIATION_WORD
```

### Callback 1 — `get_warmup_question`

- No LLM call. Returns hardcoded question:
  `"How many items can the average human hold in short-term memory?"`
- Deadline: 30s. Zero risk.

### Callback 2 — `get_round_start_info`

- No LLM call. Returns hardcoded constants from `book_config.py`.
- Context unwrap: `dynamic = ctx.get("dynamic", ctx)`
- Returns: `{book_name, book_hint, association_word}`
- Deadline: 60s. Zero risk.

### Callback 3 — `get_answers`

- Context unwrap: `dynamic = ctx.get("dynamic", ctx)`
- Iterates `dynamic["questions"]` **sequentially** (one Gemini call per question).
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
- Parse response: extract first A/B/C/D character; fallback to `"Not Relevant"` on error.
- Returns: `{"answers": [{question_number, answer}, ...]}`
- Deadline: 120s for 20 calls (~6s/call budget).

### Callback 4 — `get_score_feedback`

- Context unwrap: `dynamic = ctx.get("dynamic", ctx)`
- Access: `guess = dynamic["player_guess"]`
- Uses `self._opening_sentence` and `self._actual_word` for scoring reference.
  (Falls back to `dynamic.get("actual_opening_sentence")` and
  `dynamic.get("actual_associative_word")` if instance state is empty.)
- Single Gemini call with structured prompt requesting JSON scores (0-100 each).
- JSON schema requested from Gemini:
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
- Score → league points: `3 if >=80, 2 if >=60, 1 if >=40, else 0` (per `types.py`).
- Private score: `sent*0.5 + sent_just*0.2 + word*0.2 + word_just*0.1`
- Fallback if JSON parse fails: `difflib.SequenceMatcher` for sentence, exact match for word.
- Deadline: 180s. Low risk.

---

## Error Handling

| Callback | LLM Failure Fallback |
|---|---|
| `get_answers` | Return `"Not Relevant"` for the failed question; continue with remaining |
| `get_score_feedback` | Use string similarity fallback (difflib + exact match) |

---

## TDD Plan

Test files mirror each module:

- `test_book_config.py` — constants present, types correct, no empty strings
- `test_gemini_client.py` — mock `google.genai.Client`; test missing key raises, API error raises
- `test_student_ai.py` — mock `ask()`; test all 4 callbacks with valid ctx, test fallback paths

---

## Constraints Checklist

- [x] All files < 150 lines
- [x] TDD: tests written before implementation
- [x] `# Area:` / `# PRD:` headers in all files
- [x] No hardcoded API keys (env var `GEMINI_API_KEY`)
- [x] Context unwrap via `ctx.get("dynamic", ctx)` in all callbacks
- [x] `league_points` thresholds: 3≥80, 2≥60, 1≥40, else 0
- [x] `player_guess` accessed as nested dict
- [x] Sequential Gemini calls for `get_answers`
