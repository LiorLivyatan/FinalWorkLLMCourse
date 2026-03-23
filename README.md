# Q21G League — Final Project (AsiRoLi2025)

Multi-agent system for the Q21G League competitive 21-questions game. Includes a Player AI and a Referee AI that communicate via Gmail API.

## Quick Start

```bash
# 1. Install dependencies
pip install -e Q21G-player-whl/
pip install -e Q21G-referee-whl/

# 2. Set up environment
cp Q21G-player-whl/.env.example Q21G-player-whl/.env
# Edit .env with your API keys (OPENAI_API_KEY, GOOGLE_API_KEY)

# 3. Verify the knowledge base exists
python -c "import chromadb; c=chromadb.PersistentClient(path='./database'); print(c.get_collection('course_material').count(), 'docs')"
# Should print: 1490 docs
```

If the database doesn't exist or needs rebuilding:
```bash
PYTHONPATH=Q21G-player-whl python Q21G-player-whl/reindex_kb.py
```

## Project Structure

```
├── Q21G-player-whl/          # Player AI agent
│   ├── my_player.py          # Player callbacks (HyDE + filter + council pipeline)
│   ├── prompts*.py            # Prompt builders (questions, HyDE, deliberation, guess)
│   ├── openai_client.py       # GPT-5.4 inference client
│   ├── gemini_client.py       # Gemini inference client
│   ├── knowledge_base.py      # ChromaDB RAG interface
│   ├── candidate_filter.py    # Deterministic + LLM candidate filtering
│   ├── council.py             # Two-model deliberation council
│   ├── pdf_reader_fixed.py    # PyMuPDF PDF reader (correct RTL Hebrew)
│   ├── reindex_kb.py          # Rebuild ChromaDB from course PDFs
│   ├── run.py                 # Production entry point (Gmail polling)
│   └── TECHNICAL_REFERENCE.md # Full pipeline documentation
│
├── Q21G-referee-whl/          # Referee AI agent
│   └── examples/
│       ├── my_ai.py           # Referee callbacks (parameterizable)
│       └── book_config.py     # Tournament paragraph choice (secret)
│
├── q21_improvements/          # Evaluation & simulation tools
│   ├── generate_scenarios.py  # Random scenario generator
│   ├── run_tournament.py      # Full tournament simulation runner
│   ├── simulate_player_performance.py  # Quick eval with MockReferee
│   ├── mock_referee.py        # Lightweight RAG-connected mock referee
│   ├── tournament_analysis.ipynb       # Analysis notebook template
│   └── improvement_plan.md    # Task tracking and results history
│
├── database/                  # Pre-built ChromaDB (1490 Hebrew chunks)
├── course-material/           # Source PDFs (22 course booklets)
└── docs/                      # Specs and implementation plans
```

## Running Simulations

### Quick Evaluation (MockReferee — string similarity scoring)

Uses a lightweight mock referee with deterministic scoring. Fast, no Gemini API needed for the referee side.

```bash
# Stub mode — no API keys needed, tests pipeline structure
python q21_improvements/simulate_player_performance.py

# Real mode — uses your full player pipeline (needs OPENAI_API_KEY + GOOGLE_API_KEY)
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py
```

**Requires:** `q21_improvements/scenarios.py` with ground-truth scenarios. Copy from the template:
```bash
cp q21_improvements/scenarios.example.py q21_improvements/scenarios.py
# Edit with your own ground-truth data
```

### Tournament Simulation (Real MyRefereeAI — LLM-scored)

Full tournament with randomly generated scenarios and real LLM-based scoring (justifications evaluated, not just string similarity).

#### Step 1: Generate Scenarios

Randomly picks paragraphs from the indexed ChromaDB and uses an LLM to create rule-compliant referee metadata (hint with no paragraph words, association word category/secret pair, verbatim opening sentence).

```bash
# Default model (Gemini Flash — fast, cheap)
python q21_improvements/generate_scenarios.py

# Better model (Gemini Pro — higher quality scenarios)
python q21_improvements/generate_scenarios.py --model gemini-3.1-pro-preview
```

**Output:** `tournament_sim/scenarios_generated.json`

#### Step 2: Run Tournament

Plays each scenario through the full game flow: questions → referee answers → player guess → LLM scoring. Scores with both SDK (80/60/40) and course spec (85/70/50) thresholds.

```bash
# Full run (all scenarios, ~3 min per game)
python q21_improvements/run_tournament.py

# Quick test (first scenario only)
python q21_improvements/run_tournament.py --dry-run
```

**Output:** `tournament_sim/results.json`

#### Step 3: Analyze Results

Open the analysis notebook or generate an HTML report:

```bash
# HTML report (no jupyter needed)
python -c "
# ... (see tournament_sim/tournament_report.html generation script)
"

# Or open the notebook
jupyter notebook q21_improvements/tournament_analysis.ipynb
```

### Artifacts Location

All simulation output is stored in `tournament_sim/` (gitignored):

```
tournament_sim/
├── scenarios_generated.json   # Generated referee scenarios
├── scenarios_flash.json       # Backup: Flash-generated scenarios
├── scenarios_pro.json         # Backup: Pro-generated scenarios
├── results.json               # Tournament results with dual scoring
├── tournament_report.html     # Standalone HTML analysis report
├── reflector_analysis.md      # LLM expert analysis
└── debug_logs/                # Per-game pipeline debug logs
```

Player debug logs are in `q21_improvements/debug_logs/` (also gitignored).

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key (player inference) |
| `GOOGLE_API_KEY` | Yes | — | Google API key (embeddings + referee) |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model for player pipeline |
| `CHROMA_PATH` | No | `../database` | ChromaDB storage path |
| `GEMINI_COUNCIL_MODEL` | No | `gemini-3.1-pro-preview` | Gemini model for council deliberation |
| `GEMINI_FILTER_MODEL` | No | `gemini-3.1-flash-lite-preview` | Gemini model for LLM filter |

## Documentation

- **[TECHNICAL_REFERENCE.md](Q21G-player-whl/TECHNICAL_REFERENCE.md)** — Full pipeline documentation (architecture, setup, techniques)
- **[improvement_plan.md](q21_improvements/improvement_plan.md)** — Task history and results tracking
- **[SIMULATION_GUIDE.md](q21_improvements/SIMULATION_GUIDE.md)** — Detailed simulation usage guide
