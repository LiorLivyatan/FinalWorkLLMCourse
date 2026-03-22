# Q21 Player AI — Deliberation Pipeline Improvements

Version: 1.0.0

## Problem Statement

The MP-HyDE RAG retrieval achieves 100% recall — the correct paragraph always appears in the top 10 candidates. However, the deliberation phase picks the **wrong paragraph** 3 out of 5 times. Root causes:

1. **Attention Dilution** — A single LLM call cross-referencing 10 Hebrew paragraphs against 20 Q&A constraints takes shortcuts.
2. **Aesthetic Bias** — The LLM applies subjective preferences (e.g., favoring "thesis-like" openings) over structural evidence from the Q&A.
3. **No Hard Filtering** — Candidates that violate explicit Q&A constraints (no numbers when referee confirmed numbers exist) are still evaluated equally.

## Current Pipeline (before)

```
Questions (1 call) → MP-HyDE (1 call) → RAG → Deliberate 10 candidates (1 call) → Extract (1 call)
= 4 LLM calls, 3/5 wrong paragraph selection
```

## Proposed Pipeline (after)

```
Phase 0: Adaptive Questions (1 call, modified)
Phase 1: MP-HyDE + RAG (1 call, unchanged)
Phase 2: Hybrid Filter
  ├─ 2a. Deterministic pre-filter (0 calls)  → 10 → ~6
  └─ 2b. LLM elimination (1 cheap call)      → ~6 → 2-3
Phase 3: Two-Model Council (2 calls)
  ├─ GPT-5.4 → pick + confidence (1-10)
  └─ Gemini 3.1 Pro → pick + confidence (1-10)
Phase 4: Final Extraction (1 call, unchanged)

= 6 LLM calls total
```

## Phase 0: Adaptive Question Allocation

### What Changes

The current `build_questions_prompt()` uses a fixed 5/5/5/5 split across four orthogonal blocks (format, structure, domain, granular). The improvement folds a pre-analysis step into the same prompt: the LLM first reads the hint and association word, determines which dimensions are already known vs unknown, then allocates questions proportionally.

### Allocation Rule

- Dimensions **strongly signaled** by the hint → fewer questions (2-3)
- Dimensions **unknown** → more questions (6-7)
- Total always = 20

### Example

```
Hint: "A coding constraint whose precise threshold mirrors
       psychological research on human attention span boundaries"

Analysis: Domain is known (coding + cognitive science).
          Structure likely involves a threshold (number).
          Format and granular content are unknown.

Allocation: Format=6, Structure=6, Domain=3, Granular=5
```

### Implementation

No additional LLM call — modify `build_questions_prompt()` in `prompts.py` to include allocation instructions within the existing prompt. The existing `len(questions) != 20` validation in `my_player.py` remains unchanged — the allocation is advisory to the LLM, total must still equal 20.

## Phase 1: MP-HyDE + RAG (Unchanged)

Three Hebrew hypothetical paragraphs (conceptual, technical, rule-based) are generated and used as RAG queries alongside the original text query. Results are deduplicated to produce up to 10 unique candidates.

No changes to this phase.

## Phase 2: Hybrid Filter

### Phase 2a: Deterministic Pre-Filter

Programmatic elimination of candidates that violate hard constraints derived from Q&A answers. Zero LLM calls.

**Filter rules by block:**

| Block | Q&A Signal Example | Regex/Keyword Check |
|-------|-------------------|-------------------|
| Format | "Numbered list" | `re.search(r'^\s*[\d•\-]', text, re.MULTILINE)` |
| Format | "Code example" | `re.search(r'(def |class |import |for |if )', text)` |
| Structure | "Contains numbers/thresholds" | `re.search(r'\d{2,}', text)` |
| Structure | "References specific tech" | keyword presence (API, HTTP, Gmail, etc.) |
| Domain | Specific domain confirmed | domain keywords |
| Granular | "References figures" | `'איור' in text` or `'figure' in text` |

**Rules:**
- Only apply a filter when the answer is A, B, or C (a concrete option). Skip when answer is D ("None of these apply") — no signal.
- Not all Q&A pairs produce useful filters. Only structural/format signals are reliably checkable.
- **Hebrew content:** RAG candidates are Hebrew text with mixed English technical terms. Code patterns (`def`, `class`, `import`) still appear in mixed-language technical content. Number regex works regardless of language.
- **Safety guard:** Never filter to zero candidates. If all would be eliminated, skip the filter and pass all candidates through.

**Expected reduction:** 10 → 5-6 candidates.

### Phase 2b: LLM Elimination Round

A single call to a **fast, cheap model** (Gemini Flash or GPT-4o-mini) with a constraint-enforcement prompt:

```
Here are 6 candidate paragraphs and 20 Q&A constraints about the target paragraph.

For each candidate, check: does it VIOLATE any hard constraint?
- If the referee said "Yes, it contains numeric thresholds" and the
  candidate has no numbers → ELIMINATE
- If the referee said "No code elements" and the candidate has code → ELIMINATE
- If no violation is found → KEEP

Return ONLY a JSON list of surviving candidate indices.
```

This is not deep reasoning — it's rule enforcement. A cheap model does this reliably.

**Expected reduction:** 5-6 → 2-3 candidates.

### Implementation

New file: `Q21G-player-whl/candidate_filter.py`
- `deterministic_filter(candidates, enriched_answers) → filtered_candidates`
- `llm_elimination(candidates, enriched_answers) → filtered_candidates`

## Phase 3: Two-Model Council

### Architecture

Two models deliberate independently on the 2-3 surviving candidates. Each receives the same prompt with the same evidence (Q&A pairs + candidates) and returns:
1. The index of their chosen best candidate
2. A confidence score (1-10)
3. Brief reasoning

### Models

| Role | Model ID | Env Var | Why |
|------|----------|---------|-----|
| Primary | `gpt-5.4-2026-03-05` | `OPENAI_MODEL` | Strong reasoning, current default |
| Secondary | `gemini-2.5-pro-preview-05-06` | `GEMINI_COUNCIL_MODEL` | Different training data, different biases |
| Filter (cheap) | `gemini-3.1-flash-lite-preview` | `GEMINI_FILTER_MODEL` | Fast, cheap — already used by referee, rule enforcement only |

Models are configurable via environment variables. The Gemini council call reuses the existing `gemini_client.py` module (with model override parameter) rather than creating a new file.

### Disagreement Resolution

```
Both agree     → winner = agreed candidate
Disagree       → winner = higher confidence score
Tied confidence → winner = GPT-5.4's pick (tiebreaker)
```

### Prompt Design

Each council member receives a focused comparative prompt:

```
You are one member of a deliberation council. Compare these [2-3]
candidate paragraphs and determine which one is the target.

Evidence from 20 Q&A questions:
[enriched answers with resolved option text]

Candidate 1: [text]
Candidate 2: [text]
Candidate 3: [text]

For each candidate, evaluate:
1. Does the FORMAT match the Q&A evidence?
2. Does the CONTENT match the Q&A evidence?
3. Does it contain the structural features the answers describe?

Reply with ONLY valid JSON:
{"best_candidate_index": 0, "confidence": 8, "reasoning": "..."}
```

### Implementation

- New file: `Q21G-player-whl/council.py`
  - `council_deliberate(candidates, enriched_answers) → best_candidate`
  - Uses `openai_client.generate_json()` for GPT-5.4
  - Uses a new `gemini_generate_json()` for Gemini 3.1 Pro
- Modify `Q21G-player-whl/gemini_client.py` to add model override for council/filter calls

## Phase 4: Final Extraction (Unchanged)

The winning candidate paragraph is passed to `build_guess_prompt()` for verbatim Hebrew sentence extraction and hidden association word identification.

No changes to this phase.

## Testing Strategy

### Unit Tests (no API keys)

- `candidate_filter.py`: test deterministic filters with known Hebrew paragraphs
  - candidate with numbers survives "contains numbers" filter
  - candidate without numbers is eliminated
  - safety guard: never filter to zero
- `council.py`: test disagreement resolution logic
  - both agree → winner
  - disagree → higher confidence
  - tied confidence → GPT wins

### Integration Tests (API keys required)

- Run `SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py`
- Compare sentence scores before/after across all 5 scenarios
- Target: ≥3/5 scenarios with >60% sentence match (up from 1/5)

### Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Correct paragraph picked | 1-2/5 | 4-5/5 |
| Avg sentence score | ~45% | >65% |
| Word accuracy | 0-1/5 | 2-3/5 |
| LLM calls per game | 4-5 | 6 |

## File Changes

| File | Action | What |
|------|--------|------|
| `Q21G-player-whl/candidate_filter.py` | Create | Deterministic + LLM filtering |
| `Q21G-player-whl/council.py` | Create | Two-model council with confidence scoring |
| `Q21G-player-whl/gemini_client.py` | Modify | Add model override param for council/filter |
| `Q21G-player-whl/prompts.py` | Modify | Adaptive question allocation, council prompt, filter prompt |
| `Q21G-player-whl/my_player.py` | Modify | Wire new phases into get_guess() |
| `q21_improvements/test_deliberation.py` | Create | Filter and council unit tests (separate file to respect 150-line limit) |

## Future Considerations (Not Implemented Now)

These ideas were discussed during brainstorming and documented for potential later implementation:

### Filter-Aware Question Design
Design questions specifically so their answers are machine-filterable. Instead of "Is this academic prose?" (hard to regex), ask "Does the opening sentence contain a number greater than 10?" (trivially filterable). Creates a feedback loop where questions serve as deliberate information-gathering tools for the filter phase.

### Claude as Third Council Member
Add Claude (Anthropic API) as a third council voter for true 3-way majority voting. Eliminates all tiebreaker heuristics. Cost: +1 API call per game, only when first two models disagree.

### Agentic Reflection Loop
Instead of a single filter pass, the deliberator operates in a dynamic loop: filter → deliberate → if low confidence, re-query with more specific questions. Requires significant architectural changes.
