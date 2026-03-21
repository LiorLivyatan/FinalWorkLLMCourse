# Q21 Player Improvement & Implementation Plan

## Overview
This plan outlines the steps to dramatically improve the `MyPlayerAI` implementation. Because the tournament rules require submitting all 20 questions at once (non-adaptive questioning), a standard binary search strategy will not work. We must shift to an **Information Theory** (Orthogonal Partitioning) approach paired with advanced **RAG** (HyDE) capabilities.

## Results Summary

| Metric | Baseline (broken KB) | Current (all fixes) | Change |
|--------|---------------------|---------------------|--------|
| S1 Sentence Score | 27.2% | **86.8%** | +59.6% |
| S2 Sentence Score | 22.5% | 34.0% | +11.5% |
| S3 Sentence Score | 14.3% | 21.8% | +7.5% |
| Avg NR (lower=better) | 5.3 | **3.0** | -2.3 |
| Avg Private Score | 40.7 | **53.8** | +13.1 |
| League Points (S1/S2/S3) | 0/0/0 | **2/1/1** | +4 |
| Word Accuracy | 0% | 0% | — |

## Task 1: Building an Evaluation / Simulation Pipeline (Baseline) ✅ DONE
**Goal:** Establish a measurable baseline so we can see the exact impact of our changes without guessing.
**Implementation Tasks:**
- [x] Create a local evaluation script (`simulate_player_performance.py`) inside `q21_improvements/`.
- [x] **Data Set:** Extract 3 known opening sentences and their context paragraphs from the course materials to serve as "Ground Truth" match data (`scenarios.py`).
- [x] **Mock Referee:** Implement a RAG-connected mock referee that answers the player's 20 multiple-choice questions based on the ground truth text.
- [x] **Metrics Logging:** Calculate and log the following KPIs:
  - **Win Rate:** Percentage of games scoring ≥ 80% on the opening sentence.
  - **Word Accuracy:** Exact match rate on the association word.
  - **Information Density:** Count how many times the referee returns "Not Relevant" (a lower number means your questions were better formulated).
- [x] **Game Rules Alignment:** Fixed league points thresholds to match real game (3 if >=80, 2 if >=60, 1 if >=40).
- [x] **Simulation Guide:** Created `SIMULATION_GUIDE.md` with usage instructions for stub and real modes.

## Task 2: Advanced RAG Strategy (HyDE) ✅ DONE
**Goal:** The current player runs a vector search using ONLY the hint and book name, effectively throwing away the 20 answers received from the referee. We must use the answers to pull the right document.
**Implementation Tasks:**
- [x] **Step 1:** Create `build_hyde_prompt()` in `prompts.py`. This prompt feeds the 20 answers (with resolved option text) to Gemini and asks it to write a *synthetic, hypothetical paragraph* IN HEBREW (matching the RAG embedding space) that perfectly matches all the clues.
- [x] **Step 2:** Modify `get_guess()` so it generates this hypothetical paragraph *first*. Player stores questions between callbacks (`self._last_questions`) to resolve bare answer letters (A/B/C/D) back to option text.
- [x] **Step 3:** Pass the hypothetical text to `knowledge_base.search(query=hypothetical_text, n_results=10)`. Also searches with the original `book_name + hint + association_word` query (n=5) and deduplicates results.
- [x] **Step 4:** Ran evaluation — HyDE improved retrieval significantly after KB fix.

**Key discovery:** HyDE must generate Hebrew text because the RAG knowledge base contains Hebrew course material indexed with multilingual embeddings. English hypothetical paragraphs matched the wrong content entirely.

## Task 3: Orthogonal Question Splitting ✅ DONE
**Goal:** Stop the LLM from asking overlapping questions (e.g., asking "Is it about biology?" and then "Does it discuss living organisms?"). The 20 questions must carve the document space like a grid.
**Implementation Tasks:**
- [x] **Step 1:** Rewrote `build_questions_prompt()` in `prompts.py`. Abandoned the generic "tiers" concept.
- [x] **Step 2:** Force the LLM to assign explicit orthogonal domains to question blocks:
   - `Q1-Q5`: **Formatting and Tone** (academic, list, definition, code, etc.)
   - `Q6-Q10`: **Structural Features** (process, comparison, architecture, numbers)
   - `Q11-Q15`: **Core Domains/Entities** (software, cognitive science, protocols, agents)
   - `Q16-Q20`: **Granular Content** (thesis statement, references, metaphors, examples)
- [x] **Step 3:** Option D is always "None of these apply" — comprehensive exclusion clause.
- [x] **Step 4:** Ran evaluation — NR dropped from 5.3 to 3.0, confirming improved information density.

## Task 4: Agentic CoT (Chain of Thought) Deliberation ✅ DONE
**Goal:** The current `get_guess()` uses a single zero-shot prompt to formulate the final 100-point guess. We use multiple calls for deliberation.
**Implementation Tasks:**
- [x] **Step 1:** Added `build_deliberation_prompt()` in `prompts.py`. Scores each RAG candidate (0-100%) against the referee's answers, handling Hebrew candidates explicitly.
- [x] **Step 2:** `get_guess()` now uses two-step flow: (1) deliberate — score candidates and select best, (2) extract — final guess prompt on best candidate only.
- [x] **Step 3:** Strengthened `build_guess_prompt()` — enforces verbatim first-sentence extraction, translates Hebrew→English, guides hidden-concept word discovery.

## Task 5: Knowledge Base RTL Fix ✅ DONE (CRITICAL)
**Goal:** Fix the reversed Hebrew text in the RAG knowledge base caused by Agno's PDFReader (pypdf).
**Root Cause:** Agno's PDFReader uses `pypdf` which reads RTL glyphs in visual (left-to-right) order, reversing Hebrew character order and stripping word boundaries. e.g., `"סיכום הרצאה"` stored as `"האצרהםוכיס"`.
**Implementation Tasks:**
- [x] **Step 1:** Investigated with `test_pdf_extract.py` — confirmed PyMuPDF (`fitz`) handles RTL correctly; `python-bidi` is unnecessary.
- [x] **Step 2:** Built `test_sandbox_kb.py` — compared fixed (PyMuPDF) vs broken (Agno/pypdf) collections side by side. Confirmed the broken text was garbled.
- [x] **Step 3:** Built `pdf_reader_fixed.py` — PyMuPDF-based PDF extractor with paragraph-boundary chunking (~2000 char chunks matching original).
- [x] **Step 4:** Built `reindex_kb.py` — re-indexes all 22 course PDFs using PyMuPDF extraction + GeminiEmbedder (1536-dim, same model as original). Handles rate limits with batching and retry.
- [x] **Step 5:** Ran re-indexing: 1490 chunks indexed into `course_material` collection, replacing the broken data.
- [x] **Step 6:** Verified — S1 sentence score jumped from 27.2% to **86.8%**. This was the single largest improvement.

**Impact:** This was the most impactful fix. The player guessed "The 150-line file limit is not an arbitrary number." vs actual "The 150-line limit per file is not an arbitrary number." — only 2 words different.

## Task 6: File Structure Refactoring ✅ DONE
**Goal:** Keep all Python files under the project's 150-line limit.
- [x] Extracted all prompt builders from `my_player.py` into `prompts.py` (142 lines).
- [x] `my_player.py` reduced to 147 lines (callbacks + helpers only).
- [x] All `q21_improvements/*.py` files verified under 150 lines.

## Remaining Opportunities
- **Word accuracy** — still 0%. The model guesses related concepts (e.g., "Cognition" instead of "chunk") but not the exact hidden word. Prompt engineering on the word extraction could help.
- **S2/S3 sentence scores** — 34% and 22%. These are harder scenarios with generic opening sentences. Not critical since S1 is the real tournament paragraph.
- **Prompt tuning** — the HyDE, deliberation, and guess prompts could be further refined for Hebrew→English translation accuracy.
