# Area: Q21 Eval Pipeline
# PRD: q21_improvements/improvement_plan.md
"""
Ground-truth game scenarios for offline simulation.

All opening sentences are sourced from the Q21G League course booklet.
Scenario 1 is our referee's actual league paragraph.
"""

# ── Scenario 1: Our referee's chosen paragraph (Primary) ────────
SCENARIO_1 = {
    "name": "The Non-Arbitrary Line Limit",
    "book_name": "The Non-Arbitrary Line Limit",
    "book_hint": (
        "A coding constraint whose precise threshold mirrors psychological "
        "research on human attention span boundaries"
    ),
    "association_word": "memory",
    "actual_association_word": "chunk",
    "opening_sentence": (
        "The 150-line limit per file is not an arbitrary number."
    ),
    "warmup_answer": "7",
}

# ── Scenario 2: Guiding Design Principles (Harder) ───────────────
SCENARIO_2 = {
    "name": "System Design Principles",
    "book_name": "Q21G League Final Project",
    "book_hint": (
        "A multi-agent design separating tournament management from game "
        "refereeing to allow language-independent player implementations"
    ),
    "association_word": "protocol",
    "actual_association_word": "separation",
    "opening_sentence": (
        "The system was designed according to several guiding principles:"
    ),
    "warmup_answer": "7",
}

# ── Scenario 3: Gmail as Transport Layer (Contrasting domain) ─────
SCENARIO_3 = {
    "name": "Gmail as Agent Transport",
    "book_name": "Q21G League Final Project",
    "book_hint": (
        "An unconventional transport layer choice that trades raw speed "
        "for built-in reliability, human-readable debugging, and zero "
        "server infrastructure requirements"
    ),
    "association_word": "inbox",
    "actual_association_word": "asynchronous",
    "opening_sentence": (
        "Unlike traditional architectures that use HTTP servers, the league "
        "system uses the Gmail API as its transport layer."
    ),
    "warmup_answer": "7",
}

ALL_SCENARIOS = [SCENARIO_1, SCENARIO_2, SCENARIO_3]
