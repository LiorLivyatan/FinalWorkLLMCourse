# Area: Player AI - Question & HyDE Prompt Builders
# PRD: docs/prd-player-ai.md
"""Question generation and HyDE prompt builders for MyPlayerAI."""


def build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    """Orthogonal 4-block question prompt (20 questions).

    Uses a fixed block structure that produces rich, discriminating
    questions. Adaptive allocation was tested but degraded question
    quality — the LLM generated shallow yes/no questions instead of
    detailed analytical ones.
    """
    return f"""You are playing a 21-questions game. Generate exactly 20
multiple-choice questions to identify a specific opening sentence.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

CRITICAL RULES:
1. Questions must be ORTHOGONAL — each block covers a DIFFERENT dimension.
2. Option D must ALWAYS be: "None of these apply"
3. Options A-C must be specific and concrete, never vague.
4. Focus on narrowing WHICH PARAGRAPH, not which book.

Q1-Q5: FORMATTING & TONE (academic, list, definition, code, etc.)
Q6-Q10: STRUCTURAL (process, comparison, architecture, rule, numbers)
Q11-Q15: DOMAIN & ENTITIES (software, cognitive science, protocols, agents)
Q16-Q20: GRANULAR (thesis statement, references, metaphors, examples)

Reply with ONLY valid JSON:
{{"questions": [
  {{"question_number": 1, "question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "None of these apply"}}}},
  ...
]}}"""


def build_hyde_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict],
) -> str:
    """HyDE: synthesize a hypothetical HEBREW paragraph from Q&A answers.

    Must be Hebrew because the RAG index uses Hebrew source material
    with multilingual embeddings — Hebrew queries match best.
    """
    from prompts_deliberation import format_answer
    answers_str = "\n".join(format_answer(a) for a in answers)
    return f"""Based on a 21-questions game about a Hebrew textbook paragraph,
synthesize a hypothetical paragraph IN HEBREW that matches ALL these clues.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Question-Answer pairs:
{answers_str}

Write a 100-150 word paragraph IN HEBREW (עברית) that would be the opening
of the section this evidence points to. Use Hebrew technical terminology
that matches the hint and association word. Be specific and concrete.

The content is from an Israeli university course about multi-agent systems,
software architecture, and the Q21 League game project.

Write ONLY the Hebrew paragraph, nothing else."""


def build_mp_hyde_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict],
) -> str:
    """Analyze answers and generate 3 distinct Hebrew hypothetical paragraphs (MP-HyDE)."""
    from prompts_deliberation import format_answer
    answers_str = "\n".join(format_answer(a) for a in answers)
    return f"""Based on a 21-questions game about a Hebrew textbook, synthesize exactly 3 hypothetical paragraphs IN HEBREW that match all these clues.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Question-Answer pairs:
{answers_str}

Write 3 distinct 100-150 word paragraphs IN HEBREW (עברית). Each must imitate the EXACT academic, structured, formatting and vocabulary style of a university textbook.
- Paragraph 1: An academic conceptual overview or chapter introduction.
- Paragraph 2: A deeply granular, technical breakdown or process description.
- Paragraph 3: A strict rule definition, system limitation, or architecture description.

Use technical terminology matching the clues. Be specific and concrete.

Reply with ONLY valid JSON:
{{"paragraphs": [
  "Hebrew paragraph 1...",
  "Hebrew paragraph 2...",
  "Hebrew paragraph 3..."
]}}"""


def build_keyword_extraction_prompt(book_hint: str, association_word: str) -> str:
    """Extract concrete search keywords from the abstract hint.

    The hint is deliberately abstract. This prompt extracts the concrete
    nouns, numbers, and technical terms that would appear in the actual
    paragraph — targeting a different embedding-space region than HyDE.
    """
    return f"""Extract concrete search keywords from this hint about a
Hebrew textbook paragraph.

Hint: "{book_hint}"
Association word: "{association_word}"

Think: what specific nouns, numbers, technical terms, or Hebrew words
would LITERALLY APPEAR in the target paragraph? Not abstract concepts —
actual words you'd find in the text.

Reply with ONLY valid JSON:
{{"hebrew_keywords": "3-5 Hebrew keywords separated by spaces",
  "english_keywords": "3-5 English keywords separated by spaces"}}"""
