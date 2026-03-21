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

# Fallback feedback strings (150-200 words) used when Gemini scoring fails
FALLBACK_SENTENCE_FEEDBACK = (
    "The opening sentence score was calculated using string similarity "
    "comparison between the player's guess and the actual opening sentence. "
    "The score reflects the degree of textual overlap in terms of word choice, "
    "phrasing, and sentence structure. A higher score indicates the guess closely "
    "matched the actual sentence, while a lower score suggests the guess diverged "
    "significantly in wording or meaning. To improve, focus on identifying precise "
    "language patterns from the answers provided during the question phase."
)

FALLBACK_WORD_FEEDBACK = (
    "The associative word score was determined by exact match comparison between "
    "the player's guessed word and the actual association word chosen by the referee. "
    "An exact match yields full marks; any other word receives zero. The association "
    "word is chosen to reflect a deep thematic or conceptual connection to the "
    "source material. To improve, consider the broader intellectual domain suggested "
    "by the book hint and the pattern of answers received, then select the single "
    "word that best captures the underlying concept."
)
