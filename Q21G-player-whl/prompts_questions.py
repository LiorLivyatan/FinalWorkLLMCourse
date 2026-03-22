# Area: Player AI - Question & HyDE Prompt Builders
# PRD: docs/prd-player-ai.md
"""Question generation and HyDE prompt builders for MyPlayerAI."""


def build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    """Adaptive orthogonal question prompt (20 questions)."""
    return f"""You are playing a 21-questions game. Generate exactly 20
multiple-choice questions to identify a specific opening sentence.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

STEP 1 — ANALYZE THE HINT:
Read the hint carefully. Which dimensions does it already reveal?
- If the hint tells you the DOMAIN → ask fewer domain questions
- If the hint tells you STRUCTURAL features → ask fewer structure questions
- Allocate MORE questions to unknown dimensions

STEP 2 — GENERATE 20 QUESTIONS across these 4 blocks:
(Adjust the count per block based on Step 1. Total MUST be exactly 20.)

FORMATTING & TONE: academic, list, definition, code, etc.
STRUCTURAL: process, comparison, architecture, rule, numbers, thresholds
DOMAIN & ENTITIES: software, cognitive science, protocols, agents, databases
GRANULAR CONTENT: thesis statement, references, figures, metaphors

CRITICAL RULES:
1. Questions must be ORTHOGONAL — each block covers a DIFFERENT dimension.
2. Option D must ALWAYS be: "None of these apply"
3. Options A-C must be specific and concrete, never vague.
4. Focus on narrowing WHICH PARAGRAPH, not which book.

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
