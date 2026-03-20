# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Book constants for MyRefereeAI — Section 4.3 of the MCP Architecture book.

These are game design constants: the referee's strategic choice for this league.
ACTUAL_ASSOCIATION_WORD is intentionally hardcoded (not a runtime secret).
"""

BOOK_NAME = "The Non-Arbitrary Line Limit"

# 13 words — within the 15-word limit
BOOK_HINT = (
    "A coding constraint whose precise threshold mirrors psychological "
    "research on human attention span boundaries"
)

# Domain word shown to players
ASSOCIATION_WORD = "cognition"

# Secret word: Miller's Law — ~7 items in working memory → the 150-line rule
ACTUAL_ASSOCIATION_WORD = "seven"

# Actual opening sentence of Section 4.3
OPENING_SENTENCE = "The 150-line limit per file is not an arbitrary number."
