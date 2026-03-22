# Q21 Player AI — Technical Reference

Version: 1.0.0

This document covers the complete player AI pipeline: what was changed from the original implementation, how to set up the knowledge base, how to run simulations, and the techniques behind each stage of the player's decision-making.

---

## 1. What Changed from the Original

### Problem Statement

The original `MyPlayerAI` had three fundamental weaknesses:

1. **RAG query ignored answers** — `get_guess()` searched ChromaDB with only `book_name + hint + association_word`, throwing away the 20 answers received from the referee.
2. **Overlapping questions** — the 3-tier prompt ("chapter → paragraph → sentence") produced redundant, vague questions.
3. **Single-shot guessing** — one LLM call had to both pick the right paragraph AND extract the sentence.
4. **Broken Hebrew in the knowledge base** — Agno's PDFReader (using `pypdf`) reversed all Hebrew text, producing garbled embeddings.

### Changes Summary

| Area | Before | After |
|------|--------|-------|
| **LLM Client** | `gemini_client.py` (Gemini free tier) | `openai_client.py` (GPT-5.4) |
| **Question Strategy** | 3-tier (chapter/paragraph/sentence) | 4-block orthogonal (format, structure, domain, granular) |
| **RAG Retrieval** | Single query: `book_name + hint` | Multi-Perspective HyDE: 3 Hebrew hypothetical paragraphs + original query |
| **Guessing** | Single zero-shot prompt | Two-step: deliberation (score candidates) → extraction (guess from best) |
| **Question Storage** | Not stored between callbacks | `self._last_questions` persists for answer enrichment |
| **KB Indexing** | Agno PDFReader (pypdf, broken RTL) | PyMuPDF (`fitz`, correct RTL Hebrew) |
| **Prompt Builders** | Inline in `my_player.py` | Extracted to `prompts.py` |
| **Debugging** | None | `PhaseLogger` writes JSON per-game to `debug_logs/` |

### File Map

```
Q21G-player-whl/
├── my_player.py            # 4 PlayerAI callbacks (HyDE + CoT pipeline)
├── prompts.py              # All prompt builders (orthogonal, HyDE, deliberation, guess)
├── openai_client.py        # generate() and generate_json() via OpenAI API
├── knowledge_base.py       # ChromaDB/Agno RAG singleton (unchanged interface)
├── pdf_reader_fixed.py     # PyMuPDF PDF reader (correct RTL Hebrew)
├── reindex_kb.py           # Re-index script: PyMuPDF + GeminiEmbedder
├── gemini_client.py        # Original Gemini client (kept for reference)
└── ...
```

---

## 2. Setting Up the Knowledge Base

The player relies on a ChromaDB vector database containing all course material PDFs, correctly indexed with Hebrew text. If the database doesn't exist or needs rebuilding:

### Prerequisites

```bash
pip install pymupdf chromadb agno google-genai python-dotenv
```

### Environment Variables

Create `.env` in the project root:

```bash
GOOGLE_API_KEY=your-google-api-key      # For GeminiEmbedder (embedding model)
OPENAI_API_KEY=your-openai-api-key      # For GPT-5.4 (inference)
CHROMA_PATH=./database                  # ChromaDB storage location
COURSE_MATERIAL_PATH=./course-material  # Directory with the 22 course PDFs
```

### Building the Index

Run from the **project root** (not from `Q21G-player-whl/`):

```bash
# Dry run — verify extraction works, see chunk count
PYTHONPATH=Q21G-player-whl python Q21G-player-whl/reindex_kb.py --dry-run

# Full re-index (takes ~5 minutes, rate-limited to avoid Gemini API throttling)
PYTHONPATH=Q21G-player-whl python Q21G-player-whl/reindex_kb.py
```

This will:
1. Extract all 22 PDFs using PyMuPDF (correct RTL Hebrew)
2. Chunk into ~2000 character paragraphs at natural boundaries
3. Embed each chunk with `gemini-embedding-2-preview` (1536 dimensions)
4. Store in ChromaDB collection `course_material`
5. Write a `.indexed` flag file to prevent accidental re-indexing

### Verifying the Index

```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./database')
col = client.get_collection('course_material')
print(f'Documents: {col.count()}')  # Should be ~1490
"
```

### Why PyMuPDF Instead of Agno's PDFReader

Agno's built-in `PDFReader` uses `pypdf`, which reads RTL (right-to-left) Hebrew glyphs in visual left-to-right order. This produces reversed text:

- **pypdf output:** `האצרהםוכיס` (reversed, no spaces)
- **PyMuPDF output:** `סיכום הרצאה` (correct: "lecture summary")

The reversed text poisons both embeddings and LLM comprehension. The fix was a custom extraction pipeline using PyMuPDF (`fitz`), which handles RTL correctly out of the box.

---

## 3. Running the Simulation

The simulation pipeline lets you measure player performance offline without the League Manager or Gmail infrastructure.

### Stub Mode (No API Keys)

Tests the pipeline structure with a dummy player. Useful for verifying the simulation itself works.

```bash
python q21_improvements/simulate_player_performance.py
```

### Real Mode (API Keys Required)

Runs `MyPlayerAI` end-to-end against the `MockReferee` (which uses the real RAG + LLM to answer questions, simulating a real competitor referee).

```bash
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py
```

### What Gets Measured

| KPI | Definition | Target |
|-----|-----------|--------|
| **Win Rate** | % of games with `private_score >= 80` | >= 50% |
| **Word Accuracy** | % of games with exact association word match | >= 50% |
| **Information Density** | Avg "Not Relevant" answers per game (lower = better) | <= 5 |

### Ground Truth Scenarios

The simulation runs against 5 scenarios defined in `q21_improvements/scenarios.py`. Each has an authentic Hebrew opening sentence extracted from the actual course PDFs via PyMuPDF:

| # | Topic | Source |
|---|-------|--------|
| S1 | 150-line file limit | Section 4.3 — architectural principles |
| S2 | Prompt engineering principles | Chapter summary — prompt design |
| S3 | Gmail API constraints | Gmail API rate limits |
| S4 | Agent interaction patterns | Inter-agent communication diagram |
| S5 | Model Context Protocol | MCP architecture overview |

### Debugging a Run

Every real-mode run writes a JSON log to `q21_improvements/debug_logs/`. The log captures every pipeline phase:

```
debug_logs/
└── log_Q21G League Final Project_012814.json
    ├── phase1_questions    # The 20 questions generated
    ├── phase2_answers      # Referee answers + enriched with question text
    ├── phase3_queries      # The 3 MP-HyDE hypothetical paragraphs
    ├── phase4_candidates   # Top 10 RAG candidates (first 150 chars each)
    ├── phase5_deliberation # Candidate scoring and best selection
    └── final_guess         # The opening sentence + association word guess
```

---

## 4. Player Decision Pipeline

The player's `get_guess()` method executes a 4-step pipeline. Each step uses one LLM call.

### Step 0: Question Generation (`get_questions`)

**Technique: Orthogonal Partitioning**

Instead of the original 3-tier approach (chapter → paragraph → sentence), questions are divided into 4 orthogonal blocks that carve the document space like a grid:

| Block | Dimension | Example Question |
|-------|-----------|-----------------|
| Q1-Q5 | **Format & Tone** | "Is this academic prose, a numbered list, or a code example?" |
| Q6-Q10 | **Structure** | "Does it mention specific numbers, thresholds, or measurements?" |
| Q11-Q15 | **Domain & Entities** | "Is the topic software architecture, cognitive science, or protocols?" |
| Q16-Q20 | **Granular Content** | "Does it contain a thesis statement or reference other sections?" |

Option D is always "None of these apply" — this forces the referee to commit to a concrete answer rather than defaulting to "Not Relevant".

The questions are stored in `self._last_questions` because the real game protocol only returns answer letters (A/B/C/D) — not the question text.

### Step 1: Multi-Perspective HyDE

**Technique: Hypothetical Document Embeddings (HyDE) with Multiple Perspectives**

Standard HyDE generates one hypothetical document. MP-HyDE generates three, each from a different stylistic angle:

1. **Conceptual overview** — imitates a chapter introduction
2. **Technical breakdown** — imitates a process description or implementation detail
3. **Rule/constraint definition** — imitates a system limitation or architecture spec

All three are generated **in Hebrew** because the RAG knowledge base contains Hebrew course material indexed with multilingual embeddings. Hebrew queries produce dramatically better semantic matches than English ones.

Each hypothetical paragraph is used as a separate RAG query (`n_results=5` each), plus an additional original-text query. Results are deduplicated and merged into a candidate pool of up to 10 unique chunks.

### Step 2: RAG Search

The three MP-HyDE paragraphs + one original query produce up to 18 raw results. After deduplication by first 100 characters, the top 10 unique candidates are kept.

### Step 3: Chain-of-Thought Deliberation

**Technique: CoT Candidate Scoring**

A separate LLM call evaluates each candidate paragraph against the 20 Q&A pairs:
- Scores each candidate 0-100% on content alignment
- Selects the single best-matching paragraph
- Copies the full text of the best candidate for the final extraction step

This prevents the final guess prompt from being overwhelmed by 10 large Hebrew texts simultaneously (attention dilution).

### Step 4: Final Guess Extraction

The final LLM call receives only the best candidate paragraph and extracts:
- **opening_sentence** — the verbatim first sentence (in Hebrew, from the source text)
- **sentence_justification** — 35+ word reasoning
- **associative_word** — the hidden concept connecting the shown association word to the paragraph's thesis
- **word_justification** — 35+ word reasoning
- **confidence** — 0.0 to 1.0

### Pipeline Diagram

```
get_questions()                    get_guess()
     │                                 │
     ▼                                 ▼
┌──────────┐                  ┌─────────────────┐
│ Orthogonal│                  │ Enrich answers   │
│ 4-block   │──store──────────▶│ with stored Q's  │
│ questions │                  └────────┬────────┘
└──────────┘                           │
                                       ▼
                              ┌─────────────────┐
                              │ MP-HyDE          │  LLM call 1
                              │ 3 Hebrew hypo-   │
                              │ thetical §'s     │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ RAG Search       │  ChromaDB
                              │ 3×5 + 1×3 = 18  │
                              │ → dedup → top 10 │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ CoT Deliberation │  LLM call 2
                              │ Score candidates │
                              │ → pick best 1    │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Final Extraction │  LLM call 3
                              │ Verbatim Hebrew  │
                              │ sentence + word  │
                              └─────────────────┘
```

### LLM Call Budget

| Phase | Calls | Model |
|-------|-------|-------|
| Warmup answer | 1 | GPT-5.4 |
| Question generation | 1 | GPT-5.4 |
| MP-HyDE synthesis | 1 | GPT-5.4 |
| CoT Deliberation | 1 | GPT-5.4 |
| Final guess | 1 | GPT-5.4 |
| **Total per game** | **5** | |

The mock referee uses an additional ~20 calls (one per question via Gemini) when running in simulation mode.

---

## 5. Scoring

The referee scores the player's guess using weighted components:

| Component | Weight | What's evaluated |
|-----------|--------|-----------------|
| Opening sentence match | 50% | Similarity between guessed and actual first sentence |
| Sentence justification | 20% | Quality of the reasoning explanation |
| Association word match | 20% | Whether the hidden concept word is correct |
| Word justification | 10% | Quality of the word choice reasoning |

League points are awarded based on the weighted private score:

| Private Score | League Points |
|--------------|---------------|
| >= 80 | 3 |
| >= 60 | 2 |
| >= 40 | 1 |
| < 40 | 0 |
