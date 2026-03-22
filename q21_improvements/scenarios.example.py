# Area: Q21 Eval Pipeline
# PRD: q21_improvements/improvement_plan.md
"""
Ground-truth game scenarios for offline simulation.

Copy this file to scenarios.py and fill in your own ground-truth data
from the course material. Use find_hebrew_ground_truth.py to search
the indexed ChromaDB for authentic Hebrew opening sentences.

Usage:
    cp q21_improvements/scenarios.example.py q21_improvements/scenarios.py
    # Edit scenarios.py with your chosen paragraphs
"""

SCENARIO_1 = {
    "name": "Your Scenario Name",
    "book_name": "Q21G League Final Project",
    "book_hint": "A 15-word hint describing the paragraph...",
    "association_word": "shown_word",        # word shown to players
    "actual_association_word": "secret",      # hidden word for scoring
    "opening_sentence": "The exact Hebrew opening sentence...",
    "warmup_answer": "7",
}

# Add more scenarios for broader evaluation coverage
# SCENARIO_2 = { ... }
# SCENARIO_3 = { ... }

ALL_SCENARIOS = [SCENARIO_1]
