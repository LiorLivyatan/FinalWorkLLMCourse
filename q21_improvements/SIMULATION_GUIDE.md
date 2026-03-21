# Q21 Evaluation Simulation Guide

This document explains the technical architecture and execution instructions for the `simulate_player_performance.py` offline test harness.

## Why a Simulation?
The actual Q21 Tournament runs asynchronously over Gmail via the League Manager (`RLGMRunner`). Testing improvements to your AI Agent directly on the official infrastructure is extremely slow. This pipeline allows you to locally benchmark AI changes in seconds, tracking your "Win Rate" and "Information Density" against three reliable Ground Truth scenarios.

## Architectural Architecture
The simulation script rigorously enforces the official tournament's **Batch Format**:
1. The **Player Agent** (`MyPlayerAI`) is forced to generate all 20 multiple-choice questions blindly based only on the hint.
2. The **Referee** (`MockReferee`) evaluates all 20 questions sequentially.
3. The **Player Agent** makes a final deduction on the `opening_sentence` and `associative_word` using the referee's 20 answers.

### The Mock Referee
To accurately mock the League environment, the `MockReferee` uses an LLM (Gemini 1.5) connected to your local ChromaDB vector store (`knowledge_base.search()`). 
When your player submits questions, the referee accurately queries the database and answers A, B, C, D, or "Not Relevant"—simulating the exact logic of a true competitor referee.

## How to Run The Simulation

The script supports two execution modes.

### 1. Fast Stub Mode (No Player LLM)
If you want to quickly verify that the pipeline is working without exhausting API keys, you can run the stub mode. It uses a hardcoded fallback player (`_StubPlayer`) but uses the genuine RAG-connected referee.

```bash
# In the project root directory
python q21_improvements/simulate_player_performance.py
```

### 2. Live Agent Mode (API Required)
This mode runs your actual `MyPlayerAI` logic end-to-end. Be aware that this process requires around 60 LLM calls per run and therefore necessitates a premium billing tier (or adding `time.sleep` if operating on the free 15 RPM plan).

```bash
# In the project root directory
SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py
```

## Metrics Output
Upon completion, the framework writes its analysis to `q21_improvements/eval_results.json` and prints the following statistics to the terminal:
- **Win Rate:** The percentage of scenarios where your Player achieved a private score ≥ 80.
- **Word Accuracy:** The percentage of scenarios where the agent guessed the exact correct secret Association Word.
- **Average NR (Not Relevant):** The average number of times your questions completely missed the subject. Lower is significantly better, indicating high orthogonal accuracy.
- **Average Score (0-100):** The exact numerical score matching the official League Point thresholds.
