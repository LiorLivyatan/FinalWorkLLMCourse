# Student RefereeAI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `MyRefereeAI` in `examples/my_ai.py` — a concrete `RefereeAI` subclass that mirrors the player package's architecture: Gemini via `gemini_client.py` + Agno RAG knowledge base via `knowledge_base.py`.

**Architecture:** All student files live in `examples/` (alongside `main.py`). `gemini_client.py` mirrors the player's pattern exactly (`GOOGLE_API_KEY`, eager module-level init, `generate()` + `generate_json()`). `knowledge_base.py` uses Agno + ChromaDB + GeminiEmbedder to index the English MCP book chapters. `my_ai.py` implements all 4 callbacks; `get_answers` uses RAG search + Gemini for accurate answers.

**Tech Stack:** Python 3.x, `google-genai` (Gemini), `agno>=2.4.0` (RAG), `chromadb>=0.5.0`, `python-dotenv`, `pytest`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `examples/gemini_client.py` | Create | Gemini wrapper — mirrors player exactly |
| `examples/book_config.py` | Create | Book constants (name, hint, opening sentence, etc.) |
| `examples/knowledge_base.py` | Create | Agno RAG — indexes `chapters_en/` MCP book |
| `examples/my_ai.py` | Modify | Replace stub with full `MyRefereeAI` implementation |
| `tests/test_gemini_client.py` | Create | Tests for Gemini wrapper |
| `tests/test_book_config.py` | Create | Tests for constants |
| `tests/test_my_ai.py` | Create | Tests for all 4 callbacks (mocked) |
| `pyproject.toml` | Modify | Add `agno>=2.4.0`, `chromadb>=0.5.0` to `[llm]` deps |
| `.env.template` | Modify | Add `GOOGLE_API_KEY`, `COURSE_MATERIAL_PATH`, `CHROMA_PATH` |

**PRD/Area header for all new files:**
```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
```

**Important paths:**
- Examples directory: `examples/`
- English MCP book chapters: `../chapters_en/` (relative to `examples/`)
- ChromaDB storage: `tmp/chromadb` (default, inside `examples/`)
- Import pattern: `from my_ai import MyRefereeAI` (already in `examples/main.py`)

---

## Task 1: Install Agno + ChromaDB and update deps

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Install packages**

```bash
cd "/Users/asifamar/Desktop/Master/llm with agents/Final_project/Q21G-referee-whl"
.venv/bin/pip install "agno>=2.4.0" "chromadb>=0.5.0" "pypdf>=4.0.0"
```

- [ ] **Step 2: Update `pyproject.toml`**

Change the `[project.optional-dependencies]` section to:
```toml
[project.optional-dependencies]
llm = ["anthropic>=0.18.0", "google-genai>=1.0.0", "agno>=2.4.0", "chromadb>=0.5.0", "pypdf>=4.0.0"]
```

- [ ] **Step 3: Verify imports**

```bash
.venv/bin/python -c "import agno; import chromadb; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Update `.env.template`** — add to the LLM section:

```
GOOGLE_API_KEY=your_google_api_key_here
COURSE_MATERIAL_PATH=../chapters_en
CHROMA_PATH=./tmp/chromadb
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .env.template
git commit -m "feat: add agno/chromadb deps for RAG knowledge base"
```

---

## Task 2: `gemini_client.py` — mirror player pattern + tests (TDD)

**Files:**
- Create: `tests/test_gemini_client.py`
- Create: `examples/gemini_client.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_gemini_client.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for gemini_client — mirrors player package pattern."""
import os
import pytest
from unittest.mock import MagicMock, patch


def test_generate_returns_text(monkeypatch, tmp_path):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.text = "  hello world  "

    # Must patch at module level after env var is set
    with patch("google.genai.Client") as MockClient:
        MockClient.return_value.models.generate_content.return_value = mock_response
        # Re-import to pick up patched client
        import importlib
        import sys
        sys.modules.pop("examples.gemini_client", None)
        sys.modules.pop("gemini_client", None)

        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "gemini_client",
            pathlib.Path(__file__).parent.parent / "examples" / "gemini_client.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.generate("test prompt")

    assert result == "  hello world  "


def test_generate_json_returns_dict(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.text = '{"key": "value"}'

    with patch("google.genai.Client") as MockClient:
        MockClient.return_value.models.generate_content.return_value = mock_response
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "gemini_client",
            pathlib.Path(__file__).parent.parent / "examples" / "gemini_client.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.generate_json("test prompt")

    assert result == {"key": "value"}


def test_generate_json_returns_empty_dict_on_bad_json(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.text = "not valid json at all"

    with patch("google.genai.Client") as MockClient:
        MockClient.return_value.models.generate_content.return_value = mock_response
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "gemini_client",
            pathlib.Path(__file__).parent.parent / "examples" / "gemini_client.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.generate_json("test prompt")

    assert result == {}
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd "/Users/asifamar/Desktop/Master/llm with agents/Final_project/Q21G-referee-whl"
.venv/bin/pytest tests/test_gemini_client.py -v
```

Expected: `FileNotFoundError` or `ModuleNotFoundError`

- [ ] **Step 3: Create `examples/gemini_client.py`** — copy player pattern exactly

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Thin wrapper around Google GenAI SDK for text generation.

Uses GEMINI_MODEL and GOOGLE_API_KEY environment variables.
Exposes two functions: generate() for raw text, generate_json()
for parsed JSON responses.

Mirrors the player package's gemini_client.py pattern.
"""
import json
import os
import re

from google import genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY", ""))
_DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"


def generate(prompt: str) -> str:
    """Generate text from a prompt using Gemini."""
    model_id = os.getenv("GEMINI_MODEL", _DEFAULT_MODEL)
    response = _client.models.generate_content(
        model=model_id, contents=prompt,
    )
    return response.text


def generate_json(prompt: str) -> dict:
    """Generate a JSON response from a prompt.

    Handles markdown code blocks and returns {} on parse failure.
    """
    raw = generate(prompt)
    return _parse_json(raw)


def _parse_json(text: str) -> dict:
    """Extract and parse JSON from text, handling code blocks."""
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return {}
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/test_gemini_client.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add examples/gemini_client.py tests/test_gemini_client.py
git commit -m "feat: add gemini_client mirroring player pattern"
```

---

## Task 3: `book_config.py` — constants + tests (TDD)

**Files:**
- Create: `tests/test_book_config.py`
- Create: `examples/book_config.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_book_config.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for book_config constants."""
import importlib.util, pathlib

def load_book_config():
    spec = importlib.util.spec_from_file_location(
        "book_config",
        pathlib.Path(__file__).parent.parent / "examples" / "book_config.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_all_constants_non_empty():
    mod = load_book_config()
    for attr in ["BOOK_NAME", "BOOK_HINT", "ASSOCIATION_WORD",
                 "ACTUAL_ASSOCIATION_WORD", "OPENING_SENTENCE"]:
        val = getattr(mod, attr)
        assert isinstance(val, str) and len(val) > 0, f"{attr} is empty"


def test_hint_within_15_words():
    mod = load_book_config()
    assert len(mod.BOOK_HINT.split()) <= 15


def test_association_word_differs_from_actual():
    mod = load_book_config()
    assert mod.ASSOCIATION_WORD != mod.ACTUAL_ASSOCIATION_WORD


def test_opening_sentence_ends_with_period():
    mod = load_book_config()
    assert mod.OPENING_SENTENCE.endswith(".")
```

- [ ] **Step 2: Run to verify it fails**

```bash
.venv/bin/pytest tests/test_book_config.py -v
```

Expected: `FileNotFoundError`

- [ ] **Step 3: Create `examples/book_config.py`**

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Book constants for MyRefereeAI — Section 4.3 of the MCP Architecture book.

These are game design constants: the referee's strategic choice for this league.
ACTUAL_ASSOCIATION_WORD is intentionally hardcoded (not a runtime secret).
"""

BOOK_NAME = "The Non-Arbitrary Line Limit"

# 13 words — within the 15-word limit
BOOK_HINT = (
    "A coding constraint whose precise threshold mirrors psychological "
    "research on human attention span boundaries"
)

# Domain word shown to players
ASSOCIATION_WORD = "cognition"

# Secret word: Miller's Law — ~7 items in working memory → the 150-line rule
ACTUAL_ASSOCIATION_WORD = "seven"

# Actual opening sentence of Section 4.3
OPENING_SENTENCE = "The 150-line limit per file is not an arbitrary number."
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/test_book_config.py -v
```

Expected: 4 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add examples/book_config.py tests/test_book_config.py
git commit -m "feat: add book_config constants for Section 4.3"
```

---

## Task 4: `knowledge_base.py` — Agno RAG + tests (TDD)

**Files:**
- Create: `tests/test_knowledge_base.py`
- Create: `examples/knowledge_base.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_knowledge_base.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for knowledge_base (mocked Agno)."""
import importlib.util, pathlib
from unittest.mock import MagicMock, patch


def load_kb_module():
    spec = importlib.util.spec_from_file_location(
        "knowledge_base",
        pathlib.Path(__file__).parent.parent / "examples" / "knowledge_base.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_search_returns_list_of_dicts(monkeypatch):
    mock_doc = MagicMock()
    mock_doc.content = "The 150-line limit is based on Miller's Law."
    mock_kb = MagicMock()
    mock_kb.search.return_value = [mock_doc]

    with patch("agno.knowledge.knowledge.Knowledge", return_value=mock_kb):
        mod = load_kb_module()
        mod._knowledge = mock_kb
        results = mod.search("150-line limit", n_results=1)

    assert isinstance(results, list)
    assert results[0]["content"] == "The 150-line limit is based on Miller's Law."


def test_search_returns_empty_list_on_error(monkeypatch):
    mock_kb = MagicMock()
    mock_kb.search.side_effect = Exception("DB error")

    with patch("agno.knowledge.knowledge.Knowledge", return_value=mock_kb):
        mod = load_kb_module()
        mod._knowledge = mock_kb
        results = mod.search("anything")

    assert results == []
```

- [ ] **Step 2: Run to verify it fails**

```bash
.venv/bin/pytest tests/test_knowledge_base.py -v
```

Expected: `FileNotFoundError`

- [ ] **Step 3: Create `examples/knowledge_base.py`** — mirror player pattern

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""RAG knowledge base over the MCP Architecture book (English chapters).

Uses Agno's Knowledge + ChromaDB (local, persistent) + GeminiEmbedder.
Chapters are indexed once on first run; subsequent runs reuse the index.

Environment variables:
    CHROMA_PATH          - ChromaDB storage path (default: tmp/chromadb)
    COURSE_MATERIAL_PATH - Path to chapters_en directory (default: ../chapters_en)
    GOOGLE_API_KEY       - Required by GeminiEmbedder
"""
import os
from pathlib import Path
from typing import Optional

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_knowledge: Optional[Knowledge] = None


def _build_knowledge() -> Knowledge:
    chroma_path = os.getenv("CHROMA_PATH", "tmp/chromadb")
    return Knowledge(
        vector_db=ChromaDb(
            collection="mcp_book",
            path=chroma_path,
            persistent_client=True,
            embedder=GeminiEmbedder(
                id="gemini-embedding-2-preview",
                vertexai=True,
            ),
        ),
    )


def get_knowledge() -> Knowledge:
    global _knowledge
    if _knowledge is None:
        _knowledge = _build_knowledge()
    return _knowledge


def ensure_indexed() -> None:
    """Index MCP book chapters into ChromaDB if not already done."""
    course_path = os.getenv("COURSE_MATERIAL_PATH", "../chapters_en")
    material_dir = Path(course_path)
    if not material_dir.exists():
        return  # Skip indexing if path not configured

    chroma_path = os.getenv("CHROMA_PATH", "tmp/chromadb")
    flag_file = Path(chroma_path) / ".indexed"
    if flag_file.exists():
        return

    kb = get_knowledge()
    kb.insert(path=str(material_dir))
    flag_file.parent.mkdir(parents=True, exist_ok=True)
    flag_file.touch()


def search(query: str, n_results: int = 3) -> list[dict]:
    """Search the MCP book knowledge base."""
    try:
        kb = get_knowledge()
        documents = kb.search(query, max_results=n_results)
        return [{"content": doc.content} for doc in documents]
    except Exception:
        return []
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/pytest tests/test_knowledge_base.py -v
```

Expected: 2 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add examples/knowledge_base.py tests/test_knowledge_base.py
git commit -m "feat: add Agno knowledge_base mirroring player pattern"
```

---

## Task 5: `my_ai.py` — Full `MyRefereeAI` implementation + tests (TDD)

**Files:**
- Create: `tests/test_my_ai.py`
- Modify: `examples/my_ai.py` (replace stub with full implementation)

### Context unwrap pattern (required in ALL 4 callbacks):
```python
dynamic = ctx.get("dynamic", ctx)
```

### `player_guess` access (Callback 4 — nested dict):
```python
guess = dynamic["player_guess"]
# guess["opening_sentence"], guess["sentence_justification"],
# guess["associative_word"], guess["word_justification"]
```

### `league_points` thresholds (from types.py): 3 if >=80, 2 if >=60, 1 if >=40, else 0

- [ ] **Step 1: Write the failing tests**

Create `tests/test_my_ai.py`:

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for MyRefereeAI — all 4 callbacks."""
import json
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add examples/ to path so my_ai can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

from my_ai import MyRefereeAI
from book_config import BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD

VALID_SCORES_JSON = json.dumps({
    "opening_sentence_score": 85.0,
    "sentence_justification_score": 70.0,
    "associative_word_score": 100.0,
    "word_justification_score": 80.0,
    "opening_sentence_feedback": "Good attempt.",
    "associative_word_feedback": "Correct word!",
})


def make_warmup_ctx(wrapped=True):
    data = {"round_number": 1, "game_id": "0101001"}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_round_ctx(wrapped=True):
    data = {"round_number": 1,
            "player_a": {"id": "p1", "email": "a@x.com", "warmup_answer": "7"},
            "player_b": {"id": "p2", "email": "b@x.com", "warmup_answer": "six"}}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_questions(n=3):
    return [{"question_number": i+1, "question_text": f"Q{i+1}?",
             "options": {"A": "a", "B": "b", "C": "c", "D": "d"}} for i in range(n)]


def make_answers_ctx(questions=None, wrapped=True):
    data = {"book_name": BOOK_NAME, "book_hint": BOOK_HINT,
            "association_word": ASSOCIATION_WORD,
            "questions": questions or make_questions()}
    return {"dynamic": data, "service": {}} if wrapped else data


def make_score_ctx(wrapped=True):
    data = {"book_name": BOOK_NAME, "book_hint": BOOK_HINT,
            "association_word": ASSOCIATION_WORD,
            "actual_opening_sentence": None,
            "actual_associative_word": None,
            "player_guess": {
                "opening_sentence": "The 150-line limit is not arbitrary.",
                "sentence_justification": "Based on Miller's Law.",
                "associative_word": "seven",
                "word_justification": "7 items in memory.",
                "confidence": 0.9}}
    return {"dynamic": data, "service": {}} if wrapped else data


# ── Callback 1 ───────────────────────────────────────────────────────────────

def test_warmup_returns_question():
    ai = MyRefereeAI()
    result = ai.get_warmup_question(make_warmup_ctx())
    assert "warmup_question" in result
    assert len(result["warmup_question"]) > 0


def test_warmup_wrapped_and_raw():
    ai = MyRefereeAI()
    r1 = ai.get_warmup_question(make_warmup_ctx(wrapped=True))
    r2 = ai.get_warmup_question(make_warmup_ctx(wrapped=False))
    assert r1["warmup_question"] == r2["warmup_question"]


# ── Callback 2 ───────────────────────────────────────────────────────────────

def test_round_start_returns_book_info():
    ai = MyRefereeAI()
    result = ai.get_round_start_info(make_round_ctx())
    assert result["book_name"] == BOOK_NAME
    assert result["book_hint"] == BOOK_HINT
    assert result["association_word"] == ASSOCIATION_WORD


def test_round_start_wrapped_and_raw():
    ai = MyRefereeAI()
    r1 = ai.get_round_start_info(make_round_ctx(True))
    r2 = ai.get_round_start_info(make_round_ctx(False))
    assert r1 == r2


# ── Callback 3 ───────────────────────────────────────────────────────────────

def test_answers_happy_path():
    ai = MyRefereeAI()
    with patch("gemini_client.generate", return_value="B"), \
         patch("knowledge_base.search", return_value=[]):
        result = ai.get_answers(make_answers_ctx(make_questions(3)))
    assert len(result["answers"]) == 3
    assert all(a["answer"] in "ABCD" or a["answer"] == "Not Relevant"
               for a in result["answers"])


def test_answers_partial_failure_continues():
    ai = MyRefereeAI()
    call_count = [0]
    def side_effect(prompt):
        call_count[0] += 1
        if call_count[0] == 2:
            raise Exception("API error")
        return "C"
    with patch("gemini_client.generate", side_effect=side_effect), \
         patch("knowledge_base.search", return_value=[]):
        result = ai.get_answers(make_answers_ctx(make_questions(3)))
    answers = {a["question_number"]: a["answer"] for a in result["answers"]}
    assert answers[1] == "C"
    assert answers[2] == "Not Relevant"
    assert answers[3] == "C"


def test_answers_wrapped_and_raw():
    ai = MyRefereeAI()
    with patch("gemini_client.generate", return_value="A"), \
         patch("knowledge_base.search", return_value=[]):
        r1 = ai.get_answers(make_answers_ctx(make_questions(2), wrapped=True))
        r2 = ai.get_answers(make_answers_ctx(make_questions(2), wrapped=False))
    assert len(r1["answers"]) == len(r2["answers"])


# ── Callback 4 ───────────────────────────────────────────────────────────────

def test_score_happy_path():
    ai = MyRefereeAI()
    with patch("gemini_client.generate_json", return_value=json.loads(VALID_SCORES_JSON)):
        result = ai.get_score_feedback(make_score_ctx())
    assert result["league_points"] == 3
    assert isinstance(result["private_score"], float)
    assert set(result["breakdown"].keys()) == {
        "opening_sentence_score", "sentence_justification_score",
        "associative_word_score", "word_justification_score"}
    assert set(result["feedback"].keys()) == {"opening_sentence", "associative_word"}


def test_score_llm_failure_uses_fallback():
    ai = MyRefereeAI()
    with patch("gemini_client.generate_json", return_value={}):
        result = ai.get_score_feedback(make_score_ctx())
    assert "league_points" in result
    assert result["breakdown"]["sentence_justification_score"] == 0.0
    assert result["breakdown"]["word_justification_score"] == 0.0


def test_score_wrapped_and_raw():
    ai = MyRefereeAI()
    with patch("gemini_client.generate_json", return_value=json.loads(VALID_SCORES_JSON)):
        r1 = ai.get_score_feedback(make_score_ctx(True))
        r2 = ai.get_score_feedback(make_score_ctx(False))
    assert r1["league_points"] == r2["league_points"]


@pytest.mark.parametrize("score,pts", [
    (80.0, 3), (79.9, 2), (60.0, 2), (59.9, 1), (40.0, 1), (39.9, 0)
])
def test_league_points_boundaries(score, pts):
    ai = MyRefereeAI()
    assert ai._score_to_league_points(score) == pts
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd "/Users/asifamar/Desktop/Master/llm with agents/Final_project/Q21G-referee-whl"
.venv/bin/pytest tests/test_my_ai.py -v 2>&1 | head -20
```

Expected: ImportError (stub doesn't have full implementation)

- [ ] **Step 3: Replace `examples/my_ai.py`** with full implementation

```python
# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""
MyRefereeAI — Q21G League Referee Implementation.

Uses Gemini (via gemini_client) for LLM inference and
Agno RAG (via knowledge_base) for accurate question answering.

Book: Section 4.3 of MCP Architecture book
Strategy: Miller's Law (7 items) → association word "seven"
"""
import difflib
from typing import Any, Dict

from q21_referee import RefereeAI
import gemini_client
import knowledge_base
from book_config import (
    BOOK_NAME, BOOK_HINT, ASSOCIATION_WORD,
    ACTUAL_ASSOCIATION_WORD, OPENING_SENTENCE,
)


class MyRefereeAI(RefereeAI):
    """Referee AI using Gemini + Agno RAG. Paragraph: MCP book §4.3."""

    def __init__(self) -> None:
        self._opening_sentence = OPENING_SENTENCE
        self._actual_word = ACTUAL_ASSOCIATION_WORD

    def get_warmup_question(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        _dynamic = ctx.get("dynamic", ctx)
        return {"warmup_question":
                "How many items can the average human hold in short-term memory?"}

    def get_round_start_info(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        _dynamic = ctx.get("dynamic", ctx)
        return {"book_name": BOOK_NAME, "book_hint": BOOK_HINT,
                "association_word": ASSOCIATION_WORD}

    def get_answers(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        dynamic = ctx.get("dynamic", ctx)
        questions = dynamic.get("questions", [])
        answers = []
        for q in questions:
            answers.append({"question_number": q["question_number"],
                            "answer": self._answer_question(q)})
        return {"answers": answers}

    def get_score_feedback(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        dynamic = ctx.get("dynamic", ctx)
        guess = dynamic["player_guess"]
        scores = gemini_client.generate_json(self._build_score_prompt(guess))
        if not self._valid_scores(scores):
            scores = self._fallback_scores(guess)
        return self._build_response(scores)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _answer_question(self, q: dict) -> str:
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

    def _build_score_prompt(self, guess: dict) -> str:
        return (
            f'Score this player guess (0-100 each). Return JSON only.\n\n'
            f'ACTUAL sentence: "{self._opening_sentence}"\n'
            f'PLAYER sentence: "{guess.get("opening_sentence","")}" '
            f'(justification: "{guess.get("sentence_justification","")}")\n'
            f'ACTUAL word: "{self._actual_word}"\n'
            f'PLAYER word: "{guess.get("associative_word","")}" '
            f'(justification: "{guess.get("word_justification","")}")\n\n'
            f'{{"opening_sentence_score":0-100,'
            f'"sentence_justification_score":0-100,'
            f'"associative_word_score":0-100,'
            f'"word_justification_score":0-100,'
            f'"opening_sentence_feedback":"2-3 sentences",'
            f'"associative_word_feedback":"2-3 sentences"}}'
        )

    def _valid_scores(self, s: dict) -> bool:
        required = ["opening_sentence_score", "sentence_justification_score",
                    "associative_word_score", "word_justification_score",
                    "opening_sentence_feedback", "associative_word_feedback"]
        return all(k in s for k in required)

    def _fallback_scores(self, guess: dict) -> dict:
        def norm(t): return t.lower().strip()
        sent = difflib.SequenceMatcher(
            None, norm(self._opening_sentence),
            norm(guess.get("opening_sentence", ""))).ratio() * 100
        word = 100.0 if norm(self._actual_word) == norm(
            guess.get("associative_word", "")) else 0.0
        return {"opening_sentence_score": round(sent, 2),
                "sentence_justification_score": 0.0,
                "associative_word_score": word,
                "word_justification_score": 0.0,
                "opening_sentence_feedback": "Score via string similarity.",
                "associative_word_feedback": "Score via exact match."}

    def _build_response(self, s: dict) -> dict:
        private = (s["opening_sentence_score"] * 0.5
                   + s["sentence_justification_score"] * 0.2
                   + s["associative_word_score"] * 0.2
                   + s["word_justification_score"] * 0.1)
        return {
            "league_points": self._score_to_league_points(private),
            "private_score": round(private, 2),
            "breakdown": {k: s[k] for k in [
                "opening_sentence_score", "sentence_justification_score",
                "associative_word_score", "word_justification_score"]},
            "feedback": {
                "opening_sentence": s["opening_sentence_feedback"],
                "associative_word": s["associative_word_feedback"]},
        }

    @staticmethod
    def _score_to_league_points(score: float) -> int:
        if score >= 80: return 3
        if score >= 60: return 2
        if score >= 40: return 1
        return 0
```

- [ ] **Step 4: Run all tests**

```bash
.venv/bin/pytest tests/ -v
```

Expected: All tests PASSED

- [ ] **Step 5: Check line counts**

```bash
wc -l examples/my_ai.py examples/gemini_client.py examples/knowledge_base.py examples/book_config.py
```

Expected: Each file under 150 lines.

- [ ] **Step 6: Commit**

```bash
git add examples/my_ai.py tests/test_my_ai.py
git commit -m "feat: implement MyRefereeAI with Agno RAG and Gemini scoring"
```

---

## Done

All tests pass. Run the referee with:

```bash
cd examples
export GOOGLE_API_KEY="your-key"
export COURSE_MATERIAL_PATH="../../chapters_en"
python main.py
```
