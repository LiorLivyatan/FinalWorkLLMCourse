# Player AI Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve MyPlayerAI from 40.7 avg private score to ≥80 by implementing HyDE RAG, orthogonal questions, and CoT deliberation.

**Architecture:** Three independent improvements to `my_player.py` prompt builders and `get_guess()` flow. Each can be tested independently via `SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py`.

**Tech Stack:** Python 3.12, Gemini (via `gemini_client.py`), ChromaDB/Agno (via `knowledge_base.py`)

**Baseline:** Win Rate 0%, Word Accuracy 0%, Avg NR 5.3, Avg Score 40.7

---

## File Structure

All changes are in `Q21G-player-whl/my_player.py` (currently 153 lines). If it grows past 150 lines, extract prompt builders into `Q21G-player-whl/prompts.py`.

```
Q21G-player-whl/
├── my_player.py          # Modify: get_guess(), _build_questions_prompt(), _build_guess_prompt()
├── prompts.py            # Create if needed: extracted prompt builders
├── gemini_client.py      # Read-only: generate(), generate_json()
└── knowledge_base.py     # Read-only: search(), ensure_indexed()
```

---

### Task 1: HyDE RAG — Use answers to synthesize hypothetical paragraph

**Why:** Currently `get_guess()` searches with `book_name + hint + association_word`, completely ignoring the 20 referee answers. This is the single biggest weakness — the richest signal in the game is thrown away.

**Files:**
- Modify: `Q21G-player-whl/my_player.py`

- [ ] **Step 1: Add `_build_hyde_prompt()` function**

After the existing `_build_questions_prompt()`, add:

```python
def _build_hyde_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict],
) -> str:
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['question_text']} → {a['answer']}"
        for a in answers
    )
    return f"""Based on a 21-questions game about a book paragraph, synthesize
a hypothetical paragraph that would perfectly match ALL these clues.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Question-Answer pairs:
{answers_str}

Write a detailed 100-150 word paragraph in ENGLISH that would be the
opening of the section this evidence points to. Include specific technical
terms, concepts, and phrasing that the answers suggest. Be concrete and
specific, not vague.

Write ONLY the paragraph, nothing else."""
```

- [ ] **Step 2: Modify `get_guess()` to use HyDE**

Replace the existing RAG query in `get_guess()`:

```python
def get_guess(self, ctx: dict) -> dict:
    book_name = ctx["dynamic"].get("book_name", "Unknown")
    book_hint = ctx["dynamic"].get("book_hint", "")
    association_word = ctx["dynamic"].get("association_word", "")
    answers = ctx["dynamic"]["answers"]

    # HyDE: synthesize hypothetical paragraph from answers
    questions = ctx["dynamic"].get("questions", [])
    # Merge questions into answers for richer context
    enriched_answers = []
    for a in answers:
        q_text = ""
        for q in questions:
            if q.get("question_number") == a.get("question_number"):
                q_text = q.get("question_text", "")
                break
        enriched_answers.append({**a, "question_text": q_text})

    hyde_prompt = _build_hyde_prompt(
        book_name, book_hint, association_word, enriched_answers,
    )
    hypothetical_text = generate(hyde_prompt)

    # Search with both hypothetical text AND original query
    candidates_hyde = search(hypothetical_text, n_results=10)
    candidates_orig = search(
        f"{book_name} {book_hint} {association_word}", n_results=5,
    )

    # Deduplicate and merge
    seen = set()
    candidates = []
    for c in candidates_hyde + candidates_orig:
        key = c["content"][:100]
        if key not in seen:
            seen.add(key)
            candidates.append(c)

    candidates_text = "\n---\n".join(c["content"] for c in candidates[:10])

    prompt = _build_guess_prompt(
        book_name, book_hint, association_word,
        answers, candidates_text,
    )
    result = generate_json(prompt)
    return _validate_guess(result)
```

- [ ] **Step 3: Run simulation and compare**

```bash
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py 2>&1 | tee q21_improvements/hyde_results.txt
```

Expected: Significant improvement in opening_sentence_score (from ~21% to 50%+).

- [ ] **Step 4: Commit**

```bash
git add Q21G-player-whl/my_player.py
git commit -m "feat: add HyDE RAG — synthesize hypothetical paragraph from answers for better retrieval"
```

---

### Task 2: Orthogonal Question Splitting

**Why:** Current questions use generic "3 tiers" that produce overlapping, vague questions. The 20 questions should carve orthogonal information dimensions.

**Files:**
- Modify: `Q21G-player-whl/my_player.py` — `_build_questions_prompt()`

- [ ] **Step 1: Rewrite `_build_questions_prompt()`**

```python
def _build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    return f"""You are playing a 21-questions game. You must generate exactly 20
multiple-choice questions to identify a specific opening sentence from the book.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

CRITICAL RULES:
1. Questions must be ORTHOGONAL — each block covers a DIFFERENT dimension.
2. Option D must ALWAYS be a comprehensive exclusion: "None of these apply"
3. Options A, B, C must be specific and concrete, never vague.
4. Questions should help narrow down WHICH PARAGRAPH, not which book.

QUESTION BLOCKS (strictly follow this structure):

Q1-Q5: FORMATTING & TONE
- Is it academic prose, a case study, a list, a definition, a code example?
- Does it use first person, third person, passive voice?
- Is the tone instructional, analytical, descriptive, argumentative?

Q6-Q10: TEMPORAL & STRUCTURAL FEATURES
- Does it reference specific technologies, versions, or standards?
- Does it describe a process, a comparison, an architecture, a rule?
- Does it mention numbers, measurements, thresholds, or quantities?

Q11-Q15: CORE DOMAIN & ENTITIES
- What domain: software architecture, cognitive science, protocols, databases?
- What entities: agents, files, messages, APIs, servers, users?
- What relationships: communicates-with, contains, manages, limits?

Q16-Q20: GRANULAR CONTENT
- Does it contain a specific claim or thesis statement?
- Does it reference other sections, chapters, or figures?
- Does it use metaphors, analogies, or real-world examples?

Reply with ONLY valid JSON:
{{"questions": [
  {{"question_number": 1, "question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "None of these apply"}}}},
  ...
]}}"""
```

- [ ] **Step 2: Run simulation and compare**

```bash
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py 2>&1 | tee q21_improvements/orthogonal_results.txt
```

Expected: Lower Not Relevant count (from 5.3 to ≤3), better information density.

- [ ] **Step 3: Commit**

```bash
git add Q21G-player-whl/my_player.py
git commit -m "feat: orthogonal question splitting — 4 blocks covering format, temporal, domain, granular"
```

---

### Task 3: CoT Deliberation for Guessing

**Why:** Current guess uses a single prompt that must both select the right candidate AND extract the sentence. Splitting into two steps lets the model reason more carefully.

**Files:**
- Modify: `Q21G-player-whl/my_player.py` — `get_guess()`, add `_build_deliberation_prompt()`

- [ ] **Step 1: Add `_build_deliberation_prompt()`**

```python
def _build_deliberation_prompt(
    book_name: str, answers: list[dict], candidates_text: str,
) -> str:
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""You are evaluating candidate paragraphs for a 21-questions game.

Book: "{book_name}"

Answers received from referee:
{answers_str}

Candidate paragraphs:
{candidates_text}

For EACH candidate paragraph, score how well it matches the referee's answers
(0-100%). Consider: does the paragraph's topic, tone, structure, and content
align with what the answers suggest?

Reply with ONLY valid JSON:
{{"evaluations": [
  {{"candidate_index": 0, "score": 85, "reasoning": "..."}},
  ...
],
"best_candidate_index": 0,
"best_paragraph_text": "... (copy the full text of the best candidate)"}}"""
```

- [ ] **Step 2: Update `get_guess()` to use two-step deliberation**

After the HyDE RAG search and before the final guess prompt, add:

```python
    # Step 1: Deliberate — score candidates against answers
    deliberation_prompt = _build_deliberation_prompt(
        book_name, answers, candidates_text,
    )
    deliberation = generate_json(deliberation_prompt)
    best_text = deliberation.get("best_paragraph_text", candidates_text)

    # Step 2: Extract guess from best candidate
    prompt = _build_guess_prompt(
        book_name, book_hint, association_word,
        answers, best_text,
    )
```

- [ ] **Step 3: Strengthen `_build_guess_prompt()` for final extraction**

Update the guess prompt to be more specific about extracting the FIRST sentence:

```python
def _build_guess_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict], candidates_text: str,
) -> str:
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""You are making your FINAL GUESS in a 21-questions game.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Answers to your 20 questions:
{answers_str}

Best matching paragraph(s):
{candidates_text}

INSTRUCTIONS:
1. The "opening sentence" is the VERY FIRST sentence of the paragraph.
   Copy it EXACTLY as written — do not paraphrase, translate, or modify.
2. If the text is in Hebrew, the opening sentence is STILL the first sentence
   — copy the Hebrew text exactly.
3. The "associative_word" should be ONE ENGLISH WORD that captures the
   hidden concept connecting the association word "{association_word}"
   to the paragraph's core thesis. Think: what specific mechanism or
   concept does "{association_word}" point to?

Reply with ONLY valid JSON:
{{"opening_sentence": "... (EXACT first sentence, verbatim)",
  "sentence_justification": "... (at least 35 words)",
  "associative_word": "... (one word — the hidden concept)",
  "word_justification": "... (at least 35 words)",
  "confidence": 0.75}}"""
```

- [ ] **Step 4: Check file length, extract if needed**

```bash
wc -l Q21G-player-whl/my_player.py
```

If > 150 lines, extract all `_build_*` functions into `Q21G-player-whl/prompts.py` and import them.

- [ ] **Step 5: Run final simulation**

```bash
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py 2>&1 | tee q21_improvements/final_results.txt
```

- [ ] **Step 6: Commit**

```bash
git add Q21G-player-whl/my_player.py Q21G-player-whl/prompts.py
git commit -m "feat: CoT deliberation — two-step guess with candidate scoring"
```

---

## Expected Improvement Path

| Metric | Baseline | After HyDE | After Orthogonal | After CoT |
|--------|----------|-----------|-----------------|-----------|
| Sentence Score | 21% | 50%+ | 50%+ | 70%+ |
| Word Accuracy | 0% | 0-33% | 0-33% | 33%+ |
| Not Relevant | 5.3 | 5.3 | ≤3 | ≤3 |
| Private Score | 40.7 | 55+ | 60+ | 75+ |
