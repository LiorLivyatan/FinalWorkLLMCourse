# Area: Player AI - Prompt Builders
# PRD: docs/prd-player-ai.md
"""Prompt builders for MyPlayerAI — questions, HyDE, deliberation, guess.

IMPORTANT: The RAG knowledge base contains HEBREW course material indexed
with multilingual embeddings. HyDE must generate Hebrew to match the
embedding space. The final guess extracts the sentence in its original
language and also provides an English translation.
"""


def build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    """Orthogonal 4-block question prompt (20 questions)."""
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
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a.get('question_text', '')} → {a['answer']}"
        for a in answers
    )
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


def build_deliberation_prompt(
    book_name: str, answers: list[dict], candidates_text: str,
) -> str:
    """Score each candidate paragraph against the referee's answers.

    Candidates are likely in Hebrew — the prompt handles both languages.
    """
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""Evaluate candidate paragraphs for a 21-questions game.
The candidates may be in Hebrew — evaluate their CONTENT regardless of language.

Book: "{book_name}"

Answers received from referee:
{answers_str}

Candidate paragraphs (may be in Hebrew):
{candidates_text}

For EACH candidate, score how well its CONTENT matches the answers (0-100%).
If a candidate is in Hebrew, mentally translate it to understand the topic.

Reply with ONLY valid JSON:
{{"evaluations": [
  {{"candidate_index": 0, "score": 85, "reasoning": "..."}},
  ...
],
"best_candidate_index": 0,
"best_paragraph_text": "... (copy the FULL text of the best candidate AS-IS)"}}"""


def build_guess_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict], candidates_text: str,
) -> str:
    """Final guess extraction — handles Hebrew source, English output."""
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""You are making your FINAL GUESS in a 21-questions game.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Answers to your 20 questions:
{answers_str}

Best matching paragraph(s) — may be in Hebrew:
{candidates_text}

INSTRUCTIONS:
1. Find the VERY FIRST SENTENCE of the best matching paragraph.
2. If the paragraph is in Hebrew, TRANSLATE that first sentence to English.
   The opening_sentence in your response must be in ENGLISH.
3. Do NOT copy section numbers, table headers, or labels — only the first
   actual content sentence.
4. For "associative_word": what HIDDEN CONCEPT connects "{association_word}"
   to the paragraph's core thesis? This is NOT "{association_word}" itself.
   Think about the underlying mechanism or principle.

Reply with ONLY valid JSON:
{{"opening_sentence": "... (first sentence, in ENGLISH)",
  "sentence_justification": "... (at least 35 words explaining your reasoning)",
  "associative_word": "... (one English word — the hidden concept)",
  "word_justification": "... (at least 35 words explaining your choice)",
  "confidence": 0.75}}"""
