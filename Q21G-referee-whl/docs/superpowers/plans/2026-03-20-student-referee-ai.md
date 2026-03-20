# Student RefereeAI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `StudentRefereeAI` — a concrete `RefereeAI` subclass using Gemini to answer player questions and score guesses, with Section 4.3 of the MCP Architecture book as the chosen paragraph.

**Architecture:** Three new files under `src/q21_referee/`: `book_config.py` (constants), `gemini_client.py` (Gemini singleton wrapper), `student_ai.py` (the 4 callbacks). All callbacks unwrap context via `ctx.get("dynamic", ctx)`. `get_answers` makes one sequential Gemini call per question; `get_score_feedback` makes one batched Gemini call and falls back to difflib if JSON parsing fails.

**Tech Stack:** Python 3.x, `google-genai` (Gemini API), `difflib` (stdlib), `pytest`, `unittest.mock`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/q21_referee/book_config.py` | Create | Book name, hint, association word, secret word, opening sentence constants |
| `src/q21_referee/gemini_client.py` | Create | Module-level singleton Gemini client; single `ask(prompt)` function |
| `src/q21_referee/student_ai.py` | Create | `StudentRefereeAI` class — 4 callback methods |
| `tests/test_book_config.py` | Create | Tests for book_config constants |
| `tests/test_gemini_client.py` | Create | Tests for Gemini client (mocked API) |
| `tests/test_student_ai.py` | Create | Tests for all 4 callbacks (mocked Gemini) |
| `pyproject.toml` | Modify | Add `google-genai>=1.0.0` to `[llm]` optional deps |

**PRD/Area header for all new source files:**
```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
```

**Import path (do NOT modify `__init__.py` — it is proprietary):**
```python
from q21_referee.student_ai import StudentRefereeAI
```

---

## Task 1: Install `google-genai` and add to dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Install the package in the virtualenv**

```bash
.venv/bin/pip install "google-genai>=1.0.0"
```

Expected: Successfully installed google-genai and its dependencies.

- [ ] **Step 2: Add to `pyproject.toml` optional deps**

In `pyproject.toml`, find the `[project.optional-dependencies]` section and update the `llm` list:

```toml
[project.optional-dependencies]
llm = ["anthropic>=0.18.0", "google-genai>=1.0.0"]
```

- [ ] **Step 3: Verify import works**

```bash
.venv/bin/python -c "import google.genai; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add google-genai dependency for Gemini integration"
```

---

## Task 2: `book_config.py` — constants + tests (TDD)

**Files:**
- Create: `tests/test_book_config.py`
- Create: `src/q21_referee/book_config.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_book_config.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for book_config constants."""
from q21_referee.book_config import (
    BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD,
    ACTUAL_ASSOCIATION_WORD, OPENING_SENTENCE,
)


def test_all_constants_are_non_empty_strings():
    for value in [BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD,
                  ACTUAL_ASSOCIATION_WORD, OPENING_SENTENCE]:
        assert isinstance(value, str)
        assert len(value) > 0


def test_association_word_differs_from_actual():
    assert ASSOCIATION_WORD != ACTUAL_ASSOCIATION_WORD


def test_book_hint_is_at_most_15_words():
    assert len(BOOK_HINT.split()) <= 15


def test_opening_sentence_ends_with_period():
    assert OPENING_SENTENCE.endswith(".")
```

- [ ] **Step 2: Run to verify it fails**

```bash
.venv/bin/pytest tests/test_book_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'q21_referee.book_config'`

- [ ] **Step 3: Create `book_config.py`**

Create `src/q21_referee/book_config.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Book constants for StudentRefereeAI — Section 4.3 of the MCP Architecture book.

These are game design constants chosen by the referee's strategic game setup.
ACTUAL_ASSOCIATION_WORD is intentionally hardcoded as it is the referee's
fixed strategic choice, not a runtime secret or credential.
"""

BOOK_NAME = "The Non-Arbitrary Line Limit"

# 13 words — within the 15-word limit
BOOK_HINT = (
    "A coding constraint whose precise threshold mirrors psychological "
    "research on human attention span boundaries"
)

# Domain word shown to players
ASSOCIATION_WORD = "cognition"

# Secret word players must guess (Miller's Law: ~7 items in working memory)
ACTUAL_ASSOCIATION_WORD = "seven"

# Opening sentence of Section 4.3
OPENING_SENTENCE = "The 150-line limit per file is not an arbitrary number."
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_book_config.py -v
```

Expected: 4 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/q21_referee/book_config.py tests/test_book_config.py
git commit -m "feat: add book_config constants with tests"
```

---

## Task 3: `gemini_client.py` — Gemini wrapper + tests (TDD)

**Files:**
- Create: `tests/test_gemini_client.py`
- Create: `src/q21_referee/gemini_client.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_gemini_client.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for Gemini client wrapper."""
import os
import pytest
from unittest.mock import MagicMock, patch


def test_missing_api_key_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    # Re-import to reset module-level singleton
    import importlib
    import q21_referee.gemini_client as mod
    mod._client = None  # reset singleton
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        mod.ask("hello")


def test_successful_call_returns_stripped_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    import q21_referee.gemini_client as mod
    mod._client = None

    mock_response = MagicMock()
    mock_response.text = "  B  \n"
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client):
        mod._client = None
        result = mod.ask("some prompt")

    assert result == "B"


def test_api_exception_reraises_as_runtime_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    import q21_referee.gemini_client as mod
    mod._client = None

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("network error")

    with patch("google.genai.Client", return_value=mock_client):
        mod._client = None
        with pytest.raises(RuntimeError, match="network error"):
            mod.ask("some prompt")
```

- [ ] **Step 2: Run to verify tests fail**

```bash
.venv/bin/pytest tests/test_gemini_client.py -v
```

Expected: `ModuleNotFoundError: No module named 'q21_referee.gemini_client'`

- [ ] **Step 3: Create `gemini_client.py`**

Create `src/q21_referee/gemini_client.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Gemini API wrapper with module-level singleton client."""
import os
from typing import Optional
import google.genai

_MODEL = "gemini-3.1-flash-lite-preview"
_client: Optional[google.genai.Client] = None


def _get_client() -> google.genai.Client:
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set"
            )
        _client = google.genai.Client(api_key=key)
    return _client


def ask(prompt: str) -> str:
    """Send a prompt to Gemini and return the response text (stripped)."""
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(str(e)) from e
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_gemini_client.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/q21_referee/gemini_client.py tests/test_gemini_client.py
git commit -m "feat: add gemini_client wrapper with singleton and tests"
```

---

## Task 4: `student_ai.py` — Callbacks 1 & 2 (warmup + round start) with tests

**Files:**
- Create: `tests/test_student_ai.py` (partial — callbacks 1 & 2 only)
- Create: `src/q21_referee/student_ai.py` (partial)

- [ ] **Step 1: Write failing tests for callbacks 1 & 2**

Create `tests/test_student_ai.py` with the first two callback tests:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for StudentRefereeAI callbacks."""
import pytest
from unittest.mock import patch
from q21_referee.student_ai import StudentRefereeAI
from q21_referee.book_config import BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_warmup_ctx(wrapped=True):
    data = {"round_number": 1, "game_id": "0101001"}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_round_start_ctx(wrapped=True):
    data = {
        "round_number": 1,
        "player_a": {"id": "p1", "email": "a@x.com", "warmup_answer": "7"},
        "player_b": {"id": "p2", "email": "b@x.com", "warmup_answer": "six"},
    }
    return {"dynamic": data, "service": {}} if wrapped else data


# ── Callback 1: get_warmup_question ───────────────────────────────────────────

def test_warmup_returns_question_key():
    ai = StudentRefereeAI()
    result = ai.get_warmup_question(make_warmup_ctx())
    assert "warmup_question" in result
    assert isinstance(result["warmup_question"], str)
    assert len(result["warmup_question"]) > 0


def test_warmup_wrapped_and_raw_ctx():
    ai = StudentRefereeAI()
    r1 = ai.get_warmup_question(make_warmup_ctx(wrapped=True))
    r2 = ai.get_warmup_question(make_warmup_ctx(wrapped=False))
    assert r1["warmup_question"] == r2["warmup_question"]


# ── Callback 2: get_round_start_info ──────────────────────────────────────────

def test_round_start_returns_required_keys():
    ai = StudentRefereeAI()
    result = ai.get_round_start_info(make_round_start_ctx())
    assert result["book_name"] == BOOK_NAME
    assert result["book_hint"] == BOOK_HINT
    assert result["association_word"] == ASSOCIATION_WORD


def test_round_start_wrapped_and_raw_ctx():
    ai = StudentRefereeAI()
    r1 = ai.get_round_start_info(make_round_start_ctx(wrapped=True))
    r2 = ai.get_round_start_info(make_round_start_ctx(wrapped=False))
    assert r1 == r2


def test_round_start_wrong_player_keys_no_crash():
    """Callback 2 does not use player fields — wrong keys must not cause KeyError."""
    ai = StudentRefereeAI()
    ctx = {"dynamic": {"player1": {}, "player2": {}}, "service": {}}
    result = ai.get_round_start_info(ctx)
    assert "book_name" in result
```

- [ ] **Step 2: Run to verify tests fail**

```bash
.venv/bin/pytest tests/test_student_ai.py -v
```

Expected: `ModuleNotFoundError: No module named 'q21_referee.student_ai'`

- [ ] **Step 3: Create `student_ai.py` with callbacks 1 & 2**

Create `src/q21_referee/student_ai.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""StudentRefereeAI — concrete RefereeAI using Gemini for Q21G League."""
import re
import json
import difflib
from typing import Any, Dict

from .callbacks import RefereeAI
from .book_config import (
    BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD,
    ACTUAL_ASSOCIATION_WORD, OPENING_SENTENCE,
)
from . import gemini_client


class StudentRefereeAI(RefereeAI):
    """Concrete RefereeAI using Gemini. Paragraph: MCP book §4.3."""

    def __init__(self) -> None:
        self._opening_sentence: str = OPENING_SENTENCE
        self._actual_word: str = ACTUAL_ASSOCIATION_WORD

    # ── Callback 1 ────────────────────────────────────────────────────────────

    def get_warmup_question(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        _dynamic = ctx.get("dynamic", ctx)  # required unwrap even if unused
        return {
            "warmup_question": (
                "How many items can the average human hold in short-term memory?"
            )
        }

    # ── Callback 2 ────────────────────────────────────────────────────────────

    def get_round_start_info(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        _dynamic = ctx.get("dynamic", ctx)
        return {
            "book_name": BOOK_NAME,
            "book_hint": BOOK_HINT,
            "association_word": ASSOCIATION_WORD,
        }

    # ── Callback 3 ────────────────────────────────────────────────────────────

    def get_answers(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    # ── Callback 4 ────────────────────────────────────────────────────────────

    def get_score_feedback(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_student_ai.py -v
```

Expected: 5 tests PASSED (callbacks 1 & 2)

- [ ] **Step 5: Commit**

```bash
git add src/q21_referee/student_ai.py tests/test_student_ai.py
git commit -m "feat: implement StudentRefereeAI callbacks 1 and 2 with tests"
```

---

## Task 5: `student_ai.py` — Callback 3 (`get_answers`) with tests

**Files:**
- Modify: `tests/test_student_ai.py` (add callback 3 tests)
- Modify: `src/q21_referee/student_ai.py` (implement `get_answers`)

- [ ] **Step 1: Add failing tests for callback 3**

Append to `tests/test_student_ai.py`:

```python
# ── Callback 3: get_answers ───────────────────────────────────────────────────

def make_questions(n=3):
    return [
        {
            "question_number": i + 1,
            "question_text": f"Question {i + 1}?",
            "options": {"A": "opt A", "B": "opt B", "C": "opt C", "D": "opt D"},
        }
        for i in range(n)
    ]


def make_answers_ctx(questions=None, wrapped=True):
    data = {
        "book_name": BOOK_NAME,
        "book_hint": BOOK_HINT,
        "association_word": ASSOCIATION_WORD,
        "questions": questions or make_questions(),
    }
    return {"dynamic": data, "service": {}} if wrapped else data


def test_answers_happy_path_all_b():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value="B"):
        result = ai.get_answers(make_answers_ctx(make_questions(3)))
    assert result == {
        "answers": [
            {"question_number": 1, "answer": "B"},
            {"question_number": 2, "answer": "B"},
            {"question_number": 3, "answer": "B"},
        ]
    }


def test_answers_wrapped_and_raw_ctx():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value="A"):
        r1 = ai.get_answers(make_answers_ctx(make_questions(2), wrapped=True))
        r2 = ai.get_answers(make_answers_ctx(make_questions(2), wrapped=False))
    assert r1 == r2


def test_answers_partial_failure_continues():
    """Question 2 raises; should get Not Relevant for q2, correct for others."""
    ai = StudentRefereeAI()
    call_count = [0]

    def side_effect(prompt):
        call_count[0] += 1
        if call_count[0] == 2:
            raise RuntimeError("API error")
        return "C"

    with patch("q21_referee.gemini_client.ask", side_effect=side_effect):
        result = ai.get_answers(make_answers_ctx(make_questions(3)))

    answers = {a["question_number"]: a["answer"] for a in result["answers"]}
    assert answers[1] == "C"
    assert answers[2] == "Not Relevant"
    assert answers[3] == "C"


def test_answers_parse_failure_returns_not_relevant():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value="XYZXYZ"):
        result = ai.get_answers(make_answers_ctx(make_questions(2)))
    for a in result["answers"]:
        assert a["answer"] == "Not Relevant"
```

- [ ] **Step 2: Run to verify new tests fail**

```bash
.venv/bin/pytest tests/test_student_ai.py::test_answers_happy_path_all_b -v
```

Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: Implement `get_answers` in `student_ai.py`**

Replace the `get_answers` stub with:

```python
    def get_answers(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        dynamic = ctx.get("dynamic", ctx)
        questions = dynamic.get("questions", [])
        answers = []
        for q in questions:
            answer = self._answer_one_question(q)
            answers.append({"question_number": q["question_number"],
                            "answer": answer})
        return {"answers": answers}

    def _answer_one_question(self, q: dict) -> str:
        opts = q.get("options", {})
        prompt = (
            f'You are answering questions about this paragraph:\n'
            f'"{self._opening_sentence}"\n\n'
            f'Question: {q["question_text"]}\n'
            f'A: {opts.get("A", "")}\n'
            f'B: {opts.get("B", "")}\n'
            f'C: {opts.get("C", "")}\n'
            f'D: {opts.get("D", "")}\n\n'
            f'Answer only with A, B, C, D, or "Not Relevant".'
        )
        try:
            text = gemini_client.ask(prompt)
            for ch in text:
                if ch in "ABCD":
                    return ch
            if "Not Relevant" in text:
                return "Not Relevant"
            return "Not Relevant"
        except Exception:
            return "Not Relevant"
```

- [ ] **Step 4: Run all tests**

```bash
.venv/bin/pytest tests/test_student_ai.py -v
```

Expected: All tests PASSED (callbacks 1, 2, 3)

- [ ] **Step 5: Commit**

```bash
git add src/q21_referee/student_ai.py tests/test_student_ai.py
git commit -m "feat: implement get_answers with sequential Gemini calls and tests"
```

---

## Task 6: `student_ai.py` — Callback 4 (`get_score_feedback`) with tests

**Files:**
- Modify: `tests/test_student_ai.py` (add callback 4 tests)
- Modify: `src/q21_referee/student_ai.py` (implement `get_score_feedback`)

- [ ] **Step 1: Add failing tests for callback 4**

Append to `tests/test_student_ai.py`:

```python
# ── Callback 4: get_score_feedback ────────────────────────────────────────────

VALID_GEMINI_SCORES = json.dumps({
    "opening_sentence_score": 85.0,
    "sentence_justification_score": 70.0,
    "associative_word_score": 100.0,
    "word_justification_score": 80.0,
    "opening_sentence_feedback": "Good attempt at the sentence.",
    "associative_word_feedback": "Correct association word!",
})


def make_score_ctx(wrapped=True, actual_sentence=None, actual_word=None):
    data = {
        "book_name": BOOK_NAME,
        "book_hint": BOOK_HINT,
        "association_word": ASSOCIATION_WORD,
        "actual_opening_sentence": actual_sentence,
        "actual_associative_word": actual_word,
        "player_guess": {
            "opening_sentence": "The 150-line limit per file is not an arbitrary number.",
            "sentence_justification": "It is based on Miller's Law.",
            "associative_word": "seven",
            "word_justification": "Miller's Law says 7 items.",
            "confidence": 0.9,
        },
    }
    return {"dynamic": data, "service": {}} if wrapped else data


def test_score_happy_path():
    import json as _json
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value=VALID_GEMINI_SCORES):
        result = ai.get_score_feedback(make_score_ctx())

    assert result["league_points"] == 3  # score >= 80
    assert isinstance(result["private_score"], float)
    assert set(result["breakdown"].keys()) == {
        "opening_sentence_score", "sentence_justification_score",
        "associative_word_score", "word_justification_score",
    }
    assert set(result["feedback"].keys()) == {"opening_sentence", "associative_word"}


def test_score_wrapped_and_raw_ctx():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value=VALID_GEMINI_SCORES):
        r1 = ai.get_score_feedback(make_score_ctx(wrapped=True))
        r2 = ai.get_score_feedback(make_score_ctx(wrapped=False))
    assert r1["league_points"] == r2["league_points"]


def test_score_json_parse_failure_uses_fallback():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value="not json at all"):
        result = ai.get_score_feedback(make_score_ctx())
    assert "league_points" in result
    assert isinstance(result["private_score"], float)
    assert result["breakdown"]["sentence_justification_score"] == 0.0
    assert result["breakdown"]["word_justification_score"] == 0.0


def test_score_none_actual_sentence_uses_instance_state():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value=VALID_GEMINI_SCORES):
        result = ai.get_score_feedback(make_score_ctx(actual_sentence=None))
    assert result is not None
    assert "private_score" in result


def test_score_none_actual_word_uses_instance_state():
    ai = StudentRefereeAI()
    with patch("q21_referee.gemini_client.ask", return_value=VALID_GEMINI_SCORES):
        result = ai.get_score_feedback(make_score_ctx(actual_word=None))
    assert result is not None
    assert "private_score" in result


@pytest.mark.parametrize("score,expected_pts", [
    (80.0, 3), (79.9, 2), (60.0, 2), (59.9, 1), (40.0, 1), (39.9, 0),
])
def test_league_points_boundaries(score, expected_pts):
    ai = StudentRefereeAI()
    pts = ai._score_to_league_points(score)
    assert pts == expected_pts
```

Also add `import json` near the top of the test file.

- [ ] **Step 2: Run to verify new tests fail**

```bash
.venv/bin/pytest tests/test_student_ai.py::test_score_happy_path -v
```

Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: Implement `get_score_feedback` in `student_ai.py`**

Replace the `get_score_feedback` stub and add helpers:

```python
    def get_score_feedback(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        dynamic = ctx.get("dynamic", ctx)
        guess = dynamic["player_guess"]
        sentence_guess = guess.get("opening_sentence", "")
        sentence_just = guess.get("sentence_justification", "")
        word_guess = guess.get("associative_word", "")
        word_just = guess.get("word_justification", "")

        try:
            scores = self._score_via_gemini(
                sentence_guess, sentence_just, word_guess, word_just
            )
        except Exception:
            scores = self._score_via_fallback(sentence_guess, word_guess)

        private = (
            scores["opening_sentence_score"] * 0.5
            + scores["sentence_justification_score"] * 0.2
            + scores["associative_word_score"] * 0.2
            + scores["word_justification_score"] * 0.1
        )
        return {
            "league_points": self._score_to_league_points(private),
            "private_score": round(private, 2),
            "breakdown": {
                "opening_sentence_score": scores["opening_sentence_score"],
                "sentence_justification_score": scores["sentence_justification_score"],
                "associative_word_score": scores["associative_word_score"],
                "word_justification_score": scores["word_justification_score"],
            },
            "feedback": {
                "opening_sentence": scores["opening_sentence_feedback"],
                "associative_word": scores["associative_word_feedback"],
            },
        }

    def _score_via_gemini(self, sentence_guess, sentence_just,
                           word_guess, word_just) -> dict:
        prompt = (
            f'You are scoring a player\'s guess about a paragraph.\n\n'
            f'ACTUAL opening sentence: "{self._opening_sentence}"\n'
            f'PLAYER guessed opening sentence: "{sentence_guess}"\n'
            f'Player\'s justification for sentence: "{sentence_just}"\n\n'
            f'ACTUAL association word: "{self._actual_word}"\n'
            f'PLAYER guessed association word: "{word_guess}"\n'
            f'Player\'s justification for word: "{word_just}"\n\n'
            f'Score each component 0-100 and provide feedback (2-3 sentences each).\n'
            f'Return ONLY valid JSON with exactly these keys:\n'
            f'{{"opening_sentence_score": <float>,'
            f'"sentence_justification_score": <float>,'
            f'"associative_word_score": <float>,'
            f'"word_justification_score": <float>,'
            f'"opening_sentence_feedback": "<feedback>",'
            f'"associative_word_feedback": "<feedback>"}}'
        )
        raw = gemini_client.ask(prompt)
        clean = re.sub(r'```(?:json)?\s*|\s*```', '', raw).strip()
        return json.loads(clean)

    def _score_via_fallback(self, sentence_guess: str, word_guess: str) -> dict:
        def norm(s): return s.lower().strip()
        sent_score = difflib.SequenceMatcher(
            None, norm(self._opening_sentence), norm(sentence_guess)
        ).ratio() * 100
        word_score = 100.0 if norm(self._actual_word) == norm(word_guess) else 0.0
        return {
            "opening_sentence_score": round(sent_score, 2),
            "sentence_justification_score": 0.0,
            "associative_word_score": word_score,
            "word_justification_score": 0.0,
            "opening_sentence_feedback": "Score computed via string similarity (LLM unavailable).",
            "associative_word_feedback": "Score computed via exact match (LLM unavailable).",
        }

    @staticmethod
    def _score_to_league_points(private_score: float) -> int:
        if private_score >= 80:
            return 3
        if private_score >= 60:
            return 2
        if private_score >= 40:
            return 1
        return 0
```

- [ ] **Step 4: Run all tests**

```bash
.venv/bin/pytest tests/ -v
```

Expected: All tests PASSED (book_config + gemini_client + student_ai callbacks 1-4)

- [ ] **Step 5: Check line count on all new files**

```bash
wc -l src/q21_referee/student_ai.py src/q21_referee/gemini_client.py src/q21_referee/book_config.py
```

Expected: Each file under 150 lines.

- [ ] **Step 6: Commit**

```bash
git add src/q21_referee/student_ai.py tests/test_student_ai.py
git commit -m "feat: implement get_score_feedback with Gemini scoring, fallback, and tests"
```

---

## Task 7: Smoke test with real Gemini API (optional, skip if no key)

**Files:** none

- [ ] **Step 1: Export your key**

```bash
export GEMINI_API_KEY="your-key-here"
```

- [ ] **Step 2: Run a quick manual smoke test**

```bash
.venv/bin/python - <<'EOF'
from q21_referee.student_ai import StudentRefereeAI

ai = StudentRefereeAI()

# Test get_answers with one question
ctx = {
    "dynamic": {
        "book_name": "The Non-Arbitrary Line Limit",
        "book_hint": "A coding constraint...",
        "association_word": "cognition",
        "questions": [{
            "question_number": 1,
            "question_text": "What is the main claim of the paragraph?",
            "options": {
                "A": "The limit is random",
                "B": "The limit is based on research",
                "C": "The limit is 200 lines",
                "D": "The limit is optional"
            }
        }]
    },
    "service": {}
}
result = ai.get_answers(ctx)
print("Answers:", result)
EOF
```

Expected: `{"answers": [{"question_number": 1, "answer": "B"}]}` (or similar valid answer)

---

## Done

All tests pass, all files under 150 lines, implementation complete. Use:

```python
from q21_referee.student_ai import StudentRefereeAI

ai = StudentRefereeAI()
```
