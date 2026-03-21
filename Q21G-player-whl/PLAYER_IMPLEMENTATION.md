# Player AI Implementation

Version: 1.0.0

## Overview

RAG-based player for the Q21 League game. Uses Google Gemini for inference and a ChromaDB vector database (indexed from 22 course material PDFs) to find real opening sentences.

## Architecture

```
MyPlayerAI (my_player.py)
    ├── gemini_client.py    → Gemini inference (Google AI free tier)
    └── knowledge_base.py   → RAG search (ChromaDB + Vertex AI embeddings)
                                  │
                              database/   ← 1,252 pre-indexed document chunks
```

### Split API Strategy

| Component | API | Tier | Model |
|-----------|-----|------|-------|
| Inference | Google AI | Free | `gemini-3.1-flash-lite-preview` |
| Embeddings | Vertex AI | Paid ($300 credits) | `gemini-embedding-2-preview` |

This avoids free-tier rate limits on embeddings while keeping inference costs at zero.

## The 4 Callbacks

### 1. `get_warmup_answer(ctx)` → `{"answer": str}`
Solves a math question using Gemini. No RAG needed.

### 2. `get_questions(ctx)` → `{"questions": [...]}`
Generates 20 strategic multiple-choice questions in 3 tiers:
- **Q1-7**: Identify the chapter/broad topic
- **Q8-14**: Narrow down paragraph theme and structure
- **Q15-20**: Target specific words, phrases, or sentence patterns

### 3. `get_guess(ctx)` → `{"opening_sentence": str, ...}`
The core RAG callback:
1. Searches ChromaDB with `book_name + hint + association_word`
2. Retrieves 5 candidate paragraphs from course material
3. Prompts Gemini with Q&A answers + candidates to identify the exact opening sentence
4. Returns: sentence, justification (35+ words), association word, word justification, confidence

### 4. `on_score_received(ctx)` → `None`
Logs the score. No action needed.

## Knowledge Base

- **Source**: 22 course material PDFs (`course-material/`)
- **Vector DB**: ChromaDB at `database/` (project root, shared with referee)
- **Chunks**: 1,252 unique documents (164 from largest PDF, indexed in batches)
- **Embeddings**: Vertex AI `gemini-embedding-2-preview` (768-dim vectors)
- **Deduplication**: Flag file (`database/.indexed`) prevents re-indexing

## Scoring Weights (from referee)

| Component | Weight |
|-----------|--------|
| Opening sentence accuracy | 50% |
| Sentence justification | 20% |
| Association word match | 20% |
| Word justification | 10% |

## Files

| File | Purpose |
|------|---------|
| `my_player.py` | 4 PlayerAI callbacks (HyDE + CoT pipeline) |
| `prompts.py` | Prompt builders: orthogonal questions, HyDE, deliberation, guess |
| `gemini_client.py` | `generate()` and `generate_json()` wrappers |
| `knowledge_base.py` | ChromaDB singleton, indexing, search |
| `pdf_reader_fixed.py` | PyMuPDF PDF reader (correct RTL Hebrew extraction) |
| `reindex_kb.py` | Re-index KB: PyMuPDF + GeminiEmbedder (run from project root) |
| `test_agno_agent.py` | Agno Agent + RAG interactive test |
| `test_e2e_game.py` | Full game simulation via GameExecutor |

## Running

```bash
# From Q21G-player-whl/
source .venv/bin/activate

# Unit tests (mocked, fast)
pytest tests/unit/ -v

# Integration tests (requires API keys)
pytest tests/integration/ -v -m integration

# End-to-end game simulation
python test_e2e_game.py

# Interactive Agno Agent with RAG
python test_agno_agent.py
```

## Environment Variables

Set in `.env` at project root:

```
GOOGLE_API_KEY=...                  # Google AI API key (inference)
GEMINI_MODEL=gemini-3.1-flash-lite-preview
CHROMA_PATH=../database             # Shared ChromaDB path
COURSE_MATERIAL_PATH=../course-material
GOOGLE_CLOUD_PROJECT=...            # Vertex AI project (embeddings)
GOOGLE_CLOUD_LOCATION=us-central1
```
