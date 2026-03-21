# Q21 Player Improvement & Implementation Plan

## Overview
This plan outlines the steps to dramatically improve the `MyPlayerAI` implementation. Because the tournament rules require submitting all 20 questions at once (non-adaptive questioning), a standard binary search strategy will not work. We must shift to an **Information Theory** (Orthogonal Partitioning) approach paired with advanced **RAG** (HyDE) capabilities.

## Task 1: Building an Evaluation / Simulation Pipeline (Baseline)
**Goal:** Establish a measurable baseline so we can see the exact impact of our changes without guessing.
**Implementation Tasks:**
- [x] Create a local evaluation script (`simulate_player_performance.py`) inside `q21_improvements/`.
- [x] **Data Set:** Extract 3 known opening sentences and their context paragraphs from the course materials to serve as "Ground Truth" match data (`scenarios.py`).
- [x] **Mock Referee:** Implement a RAG-connected mock referee that answers the player's 20 multiple-choice questions based on the ground truth text.
- [x] **Metrics Logging:** Calculate and log the following KPIs:
  - **Win Rate:** Percentage of games scoring ≥ 80% on the opening sentence.
  - **Word Accuracy:** Exact match rate on the association word.
  - **Information Density:** Count how many times the referee returns "Not Relevant" (a lower number means your questions were better formulated).

## Task 2: Advanced RAG Strategy (HyDE)
**Goal:** The current player runs a vector search using ONLY the hint and book name, effectively throwing away the 20 answers received from the referee. We must use the answers to pull the right document.
**Implementation Tasks:**
- [ ] **Step 1:** Create `_build_hyde_prompt()` in `my_player.py`. This prompt will feed the 20 answers to Gemini and ask it to write a *synthetic, hypothetical paragraph* that perfectly matches all the clues.
- [ ] **Step 2:** Modify `get_guess()` so it generates this hypothetical paragraph *first*.
- [ ] **Step 3:** Pass the requested hypothetical text to `knowledge_base.search(query=hypothetical_text, n_results=10)`. Increasing the results pool to 10 ensures safety against edge cases.
- [ ] **Step 4:** Run the evaluation script (`Task 1`). We should immediately see a massive bump in opening sentence accuracy because the LLM is now looking at the right paragraphs.

## Task 3: Orthogonal Question Splitting
**Goal:** Stop the LLM from asking overlapping questions (e.g., asking "Is it about biology?" and then "Does it discuss living organisms?"). The 20 questions must carve the document space like a grid.
**Implementation Tasks:**
- [ ] **Step 1:** Rewrite `_build_questions_prompt()`. Abandon the generic "tiers" concept.
- [ ] **Step 2:** Force the LLM to assign explicit orthogonal domains to question blocks:
   - `Q1-Q5`: **Formatting and Tone** (Is it academic, a case study, empirical data, theoretical equations?).
   - `Q6-Q10`: **Temporal/Spatial features** (Historical eras, specific regions, or physical scales).
   - `Q11-Q15`: **Core Domains/Entities** (Abstract concepts vs. Concrete hardware/biology vs. Human psychology).
   - `Q16-Q20`: **Granular Structure** (Does the paragraph contain statistics, definitions, or citations?).
- [ ] **Step 3:** Demand that 'Option D' is always a comprehensive exclusion clause (e.g., "None of the above - Strictly X") so the referee is mathematically forced to pick a letter and never falls back to "Not Relevant". 
- [ ] **Step 4:** Run the evaluation script again to observe improvement in the "Information Density" metric.

## Task 4: Agentic CoT (Chain of Thought) Deliberation
**Goal:** The current `get_guess()` uses a single zero-shot prompt to formulate the final 100-point guess. The free Gemini limit accommodates multiple calls. We should use it for deliberation.
**Implementation Tasks:**
- [ ] **Step 1:** Add an intermediate LLM call in `get_guess()`. Ask the model to conceptually evaluate the 10 RAG candidates and score them against the 20 answers (`Candidate 1 vs Answers = 85% match`).
- [ ] **Step 2:** Isolate the highest-scoring candidate text, and use a *second* LLM call to extract the exact `opening_sentence` and heavily deliberate on the hidden association `associative_word`.
