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

# Domain word shown to players: memory is a genuine category that contains "chunk"
ASSOCIATION_WORD = "memory"

# Secret word: Miller's Law — working memory operates via chunking → "chunk"
ACTUAL_ASSOCIATION_WORD = "chunk"

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
    "word is grounded in Miller's Law: working memory processes information by grouping "
    "items into meaningful units — a mechanism known as chunking. The 150-line file limit "
    "is calibrated to the size of a cognitive chunk a developer can hold in working memory. "
    "To improve, reason from the memory domain through cognitive psychology to the specific "
    "mechanism that connects memory capacity to the paragraph's central claim."
)
