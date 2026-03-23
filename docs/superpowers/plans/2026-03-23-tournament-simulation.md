# Tournament Simulation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate 10 realistic referee scenarios from course PDFs following all official rules, run the full player pipeline against them using real MyRefereeAI (LLM-scored), and produce an analysis notebook with expert insights.

**Architecture:** A scenario generator randomly samples ChromaDB chunks and uses Gemini to produce rule-compliant referee metadata. A tournament runner wires MyPlayerAI vs a parameterized MyRefereeAI for each scenario. A Jupyter notebook loads results and uses GPT-5.4 as a reflector to produce narrative analysis.

**Tech Stack:** Python 3.12, ChromaDB, Gemini Flash (referee), GPT-5.4 + Gemini Pro (player council), Jupyter, pytest

**Spec:** `docs/superpowers/specs/2026-03-23-tournament-simulation-design.md`

**Expert Skills:**
- `q21-referee-simulator` — domain knowledge for scenario generation
- `q21-results-reflector` — domain knowledge for results analysis

---

## File Structure

```
q21_improvements/
├── generate_scenarios.py          # NEW: random scenario generator
├── run_tournament.py              # NEW: full simulation runner
├── tournament_analysis.ipynb      # NEW: notebook template
├── test_tournament.py             # NEW: unit tests
└── tournament_sim/                # ALL OUTPUT (gitignored)

Q21G-referee-whl/examples/
├── my_ai.py                       # MODIFY: accept optional scenario dict
└── knowledge_base.py              # MODIFY: flag-first ensure_indexed
```

---

### Task 0: Fix referee knowledge_base.py and parameterize MyRefereeAI

**Files:**
- Modify: `Q21G-referee-whl/examples/knowledge_base.py`
- Modify: `Q21G-referee-whl/examples/my_ai.py`

- [ ] **Step 1: Fix ensure_indexed() — check flag before course path**

In `Q21G-referee-whl/examples/knowledge_base.py`, reorder `ensure_indexed()` so the `.indexed` flag check comes BEFORE the `COURSE_MATERIAL_PATH` existence check. This prevents `FileNotFoundError` when using the pre-built PyMuPDF-indexed database.

```python
def ensure_indexed() -> None:
    chroma_path = os.getenv("CHROMA_PATH", "../database")
    flag_file = Path(chroma_path) / ".indexed"
    if flag_file.exists():
        return
    # Only check course path if we need to index
    course_path = os.getenv("COURSE_MATERIAL_PATH", "../chapters_en")
    material_dir = Path(course_path)
    if not material_dir.exists():
        raise FileNotFoundError(...)
    kb = get_knowledge()
    kb.insert(path=str(material_dir))
    flag_file.parent.mkdir(parents=True, exist_ok=True)
    flag_file.touch()
```

- [ ] **Step 2: Parameterize MyRefereeAI**

Modify `__init__` in `Q21G-referee-whl/examples/my_ai.py` to accept an optional scenario dict:

```python
def __init__(self, scenario: dict = None) -> None:
    if scenario:
        self._opening_sentence = scenario["opening_sentence"]
        self._actual_word = scenario["actual_association_word"]
        self._book_name = scenario.get("book_name", BOOK_NAME)
        self._book_hint = scenario.get("book_hint", BOOK_HINT)
        self._association_word = scenario.get("association_word", ASSOCIATION_WORD)
    else:
        self._opening_sentence = OPENING_SENTENCE
        self._actual_word = ACTUAL_ASSOCIATION_WORD
        self._book_name = BOOK_NAME
        self._book_hint = BOOK_HINT
        self._association_word = ASSOCIATION_WORD
    knowledge_base.ensure_indexed()
```

Update `get_round_start_info` to use instance vars:
```python
def get_round_start_info(self, ctx):
    return {"book_name": self._book_name, "book_hint": self._book_hint,
            "association_word": self._association_word}
```

- [ ] **Step 3: Verify default behavior unchanged**

Run: `cd Q21G-referee-whl/examples && CHROMA_PATH=../../database python -c "from my_ai import MyRefereeAI; r = MyRefereeAI(); print(r.get_round_start_info({}))" `
Expected: original book_config values

- [ ] **Step 4: Commit**

```bash
git add Q21G-referee-whl/examples/my_ai.py Q21G-referee-whl/examples/knowledge_base.py
git commit -m "feat: parameterize MyRefereeAI + fix referee KB flag-first check"
```

---

### Task 1: Build scenario generator

**Skill:** Use `q21-referee-simulator` skill for domain knowledge about rules and constraints.

**Files:**
- Create: `q21_improvements/generate_scenarios.py`
- Create: `q21_improvements/test_tournament.py`

- [ ] **Step 1: Write test for hint validation**

```python
# q21_improvements/test_tournament.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))

def test_hint_has_no_paragraph_words():
    from q21_improvements.generate_scenarios import validate_hint
    paragraph = "מגבלת150שורות לקובץ היא לא מספר שרירותי."
    good_hint = "architectural constraint reflecting cognitive load thresholds"
    bad_hint = "מגבלת שורות לקובץ coding rule"
    assert validate_hint(good_hint, paragraph) == True
    assert validate_hint(bad_hint, paragraph) == False

def test_hint_word_count():
    from q21_improvements.generate_scenarios import validate_hint
    short = "a b c"
    long = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"
    assert validate_hint(short, "irrelevant") == True
    assert validate_hint(long, "irrelevant") == False
```

- [ ] **Step 2: Implement generate_scenarios.py**

The script:
1. Connects to ChromaDB at `./database`
2. Randomly samples 10 chunks using `collection.get(offset=random, limit=1)`
3. For each chunk, calls Gemini Flash to generate referee metadata
4. Validates hint (no paragraph words, ≤15 words)
5. Retries up to 3 times if validation fails
6. Saves to `tournament_sim/scenarios_generated.json`

```python
# q21_improvements/generate_scenarios.py
"""Generate 10 random referee scenarios from ChromaDB course material."""
import json, os, sys, random, re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

import chromadb
from gemini_client import generate_json  # uses player's gemini_client (has temperature param)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "tournament_sim")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./database")
STOP_WORDS = {"של", "את", "על", "עם", "הם", "היא", "הוא", "זה", "זו",
              "כי", "אם", "לא", "גם", "כל", "בין", "אחד", "יש", "אין",
              "the", "a", "an", "is", "are", "in", "on", "of", "and", "or"}


def validate_hint(hint: str, paragraph: str) -> bool:
    if len(hint.split()) > 15:
        return False
    para_words = {w.lower() for w in re.findall(r'[\w\u0590-\u05FF]{3,}', paragraph)}
    hint_words = {w.lower() for w in re.findall(r'[\w\u0590-\u05FF]{3,}', hint)}
    overlap = (para_words & hint_words) - STOP_WORDS
    return len(overlap) == 0


def _build_referee_prompt(chunk_text: str) -> str:
    return f"""You are a Q21 League referee. Given this Hebrew paragraph from a university textbook, generate game metadata.

Paragraph:
{chunk_text}

Rules:
1. book_name: creative title, up to 5 words
2. book_hint: up to 15 words, NO WORDS from the paragraph (this is critical)
3. association_word: the CATEGORY shown to players (e.g., "memory", "limits")
4. actual_association_word: the SECRET specific concept players must guess
5. opening_sentence: the EXACT verbatim first sentence from the paragraph
6. warmup_question: a simple math problem (e.g., "What is 8 * 7?")

Reply with ONLY valid JSON:
{{"book_name": "...", "book_hint": "...", "association_word": "...",
  "actual_association_word": "...", "opening_sentence": "...",
  "warmup_question": "..."}}"""


def generate_scenarios(n: int = 10) -> list:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    col = client.get_collection("course_material")
    total = col.count()
    scenarios = []

    for i in range(n):
        for attempt in range(3):
            offset = random.randint(0, total - 1)
            result = col.get(offset=offset, limit=1,
                           include=["documents", "metadatas"])
            chunk = result["documents"][0]
            meta = result["metadatas"][0]

            prompt = _build_referee_prompt(chunk)
            data = generate_json(prompt, temperature=0.0)

            if not data.get("opening_sentence"):
                continue

            hint = data.get("book_hint", "")
            if validate_hint(hint, chunk):
                scenarios.append({
                    "id": i + 1,
                    "source_pdf": meta.get("name", "unknown"),
                    "source_page": meta.get("page", 0),
                    **data,
                    "full_paragraph": chunk,
                })
                break
        else:
            print(f"Warning: scenario {i+1} failed after 3 attempts")

    return scenarios


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    scenarios = generate_scenarios(10)
    out_path = os.path.join(OUTPUT_DIR, "scenarios_generated.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(scenarios)} scenarios → {out_path}")
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest q21_improvements/test_tournament.py -v`
Expected: 2 PASSED

- [ ] **Step 4: Commit**

```bash
git add q21_improvements/generate_scenarios.py q21_improvements/test_tournament.py
git commit -m "feat: random referee scenario generator with hint validation"
```

---

### Task 2: Build tournament runner

**Files:**
- Create: `q21_improvements/run_tournament.py`

- [ ] **Step 1: Implement run_tournament.py**

The runner:
1. Loads `tournament_sim/scenarios_generated.json`
2. For each scenario, creates `MyRefereeAI(scenario)` and `MyPlayerAI()`
3. Runs the full game flow with proper `ctx` dicts
4. Scores with BOTH threshold sets
5. Saves all results to `tournament_sim/results.json`

Key implementation details:
- Import MyRefereeAI with sys.path manipulation (it lives in Q21G-referee-whl/examples/)
- Build `ctx` dicts matching the format from `context_builder.py`
- Dual scoring function:

```python
def _dual_score(private_score):
    return {
        "sdk": {"3": private_score >= 80, "2": private_score >= 60,
                "1": private_score >= 40, "points": (3 if private_score >= 80 else 2 if private_score >= 60 else 1 if private_score >= 40 else 0)},
        "spec": {"3": private_score >= 85, "2": private_score >= 70,
                 "1": private_score >= 50, "points": (3 if private_score >= 85 else 2 if private_score >= 70 else 1 if private_score >= 50 else 0)},
    }
```

- Each game is independent — catch exceptions and continue
- Include sleep between games for rate limit safety

- [ ] **Step 2: Test with dry run (1 scenario)**

Run: `python q21_improvements/run_tournament.py --dry-run`
(Implement `--dry-run` flag that runs only scenario 1)

- [ ] **Step 3: Commit**

```bash
git add q21_improvements/run_tournament.py
git commit -m "feat: tournament runner with dual scoring and real MyRefereeAI"
```

---

### Task 3: Update .gitignore and add tournament_sim/

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add tournament_sim to gitignore**

```
# Tournament simulation output
q21_improvements/tournament_sim/
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore tournament_sim output directory"
```

---

### Task 4: Create analysis notebook

**Skill:** Use `q21-results-reflector` skill for the reflector prompt and analysis structure.

**Files:**
- Create: `q21_improvements/tournament_analysis.ipynb`

- [ ] **Step 1: Create notebook template**

The notebook should have these cells:

1. **Setup cell** — loads `tournament_sim/results.json` and `scenarios_generated.json`
2. **Scenario overview** — pandas table of all 10 scenarios
3. **Per-scenario results** — sentence score, word match, NR, league points (both thresholds)
4. **Aggregate KPIs** — avg score, win rate, word accuracy, avg NR
5. **Pipeline diagnostics** — RAG hit rate, filter survival, council agreement from debug logs
6. **Scoring comparison** — SDK vs spec thresholds side-by-side
6. **LLM Reflector cell** — calls GPT-5.4 with the `q21-results-reflector` skill prompt, passing the full results JSON. Renders the narrative analysis as markdown.

The reflector prompt should:
- Classify each scenario into a failure mode (RAG miss / filter kill / council misjudge / extraction error / word miss / success)
- Identify patterns across the 10 scenarios
- Produce 3-5 actionable recommendations ranked by expected impact

- [ ] **Step 2: Commit**

```bash
git add q21_improvements/tournament_analysis.ipynb
git commit -m "feat: tournament analysis notebook with LLM reflector"
```

---

### Task 5: Generate scenarios + run full tournament

- [ ] **Step 1: Generate 10 scenarios**

```bash
python q21_improvements/generate_scenarios.py
```

Expected: `tournament_sim/scenarios_generated.json` with 10 entries

- [ ] **Step 2: Run full tournament**

```bash
SIMULATE_REAL=1 python q21_improvements/run_tournament.py
```

Expected: `tournament_sim/results.json` with 10 game results + dual scoring

- [ ] **Step 3: Run notebook**

Open and execute `q21_improvements/tournament_analysis.ipynb`.
Verify reflector produces narrative insights.

- [ ] **Step 4: Commit and push**

```bash
git push
```
