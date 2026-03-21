# Area: Player AI - Prompt Builders
# PRD: docs/prd-player-ai.md
"""Prompt builders for MyPlayerAI — questions, HyDE, deliberation, guess."""


def build_questions_prompt(
    book_name: str, book_hint: str, association_word: str,
) -> str:
    """Orthogonal 4-block question prompt (20 questions)."""
    return f"""You are playing a 21-questions game. Generate exactly 20
multiple-choice questions to identify a specific opening sentence from the book.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

CRITICAL RULES:
1. Questions must be ORTHOGONAL — each block covers a DIFFERENT dimension.
2. Option D must ALWAYS be: "None of these apply"
3. Options A, B, C must be specific and concrete, never vague.
4. Focus on narrowing down WHICH PARAGRAPH, not which book.

QUESTION BLOCKS:

Q1-Q5: FORMATTING & TONE
- Academic prose, case study, list, definition, or code example?
- First person, third person, passive voice?
- Instructional, analytical, descriptive, or argumentative?

Q6-Q10: TEMPORAL & STRUCTURAL FEATURES
- References specific technologies, versions, or standards?
- Describes a process, comparison, architecture, or rule?
- Mentions numbers, measurements, thresholds, or quantities?

Q11-Q15: CORE DOMAIN & ENTITIES
- Domain: software architecture, cognitive science, protocols, databases?
- Entities: agents, files, messages, APIs, servers, users?
- Relationships: communicates-with, contains, manages, limits?

Q16-Q20: GRANULAR CONTENT
- Contains a specific claim or thesis statement?
- References other sections, chapters, or figures?
- Uses metaphors, analogies, or real-world examples?

Reply with ONLY valid JSON:
{{"questions": [
  {{"question_number": 1, "question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "None of these apply"}}}},
  ...
]}}"""


def build_hyde_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict],
) -> str:
    """HyDE: synthesize a hypothetical paragraph from Q&A answers."""
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a.get('question_text', '')} → {a['answer']}"
        for a in answers
    )
    return f"""Based on a 21-questions game about a book paragraph, synthesize
a hypothetical paragraph that would perfectly match ALL these clues.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Question-Answer pairs:
{answers_str}

Write a detailed 100-150 word paragraph in ENGLISH that would be the
opening of the section this evidence points to. Include specific technical
terms, concepts, and phrasing that the answers suggest. Be concrete.

Write ONLY the paragraph, nothing else."""


def build_deliberation_prompt(
    book_name: str, answers: list[dict], candidates_text: str,
) -> str:
    """Score each candidate paragraph against the referee's answers."""
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""Evaluate candidate paragraphs for a 21-questions game.

Book: "{book_name}"

Answers received from referee:
{answers_str}

Candidate paragraphs:
{candidates_text}

For EACH candidate, score how well it matches the answers (0-100%).
Consider: does the paragraph's topic, tone, structure, and content
align with what the answers suggest?

Reply with ONLY valid JSON:
{{"evaluations": [
  {{"candidate_index": 0, "score": 85, "reasoning": "..."}},
  ...
],
"best_candidate_index": 0,
"best_paragraph_text": "... (copy the FULL text of the best candidate)"}}"""


def build_guess_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict], candidates_text: str,
) -> str:
    """Final guess extraction from the best candidate paragraph."""
    answers_str = "\n".join(
        f"Q{a['question_number']}: {a['answer']}" for a in answers
    )
    return f"""You are making your FINAL GUESS in a 21-questions game.

Book: "{book_name}"
Hint: "{book_hint}"
Association word: "{association_word}"

Answers to your 20 questions:
{answers_str}

Best matching paragraph(s):
{candidates_text}

INSTRUCTIONS:
1. The "opening sentence" is the VERY FIRST sentence of the paragraph.
   Copy it EXACTLY as written — do not paraphrase, translate, or modify.
2. If the text is in Hebrew, copy the Hebrew text exactly as the opening sentence.
3. For "associative_word": think about what HIDDEN CONCEPT connects the
   association word "{association_word}" to the paragraph's core thesis.
   This is NOT "{association_word}" itself — it's the specific mechanism
   or concept that "{association_word}" points to.

Reply with ONLY valid JSON:
{{"opening_sentence": "... (EXACT first sentence, verbatim)",
  "sentence_justification": "... (at least 35 words)",
  "associative_word": "... (one word — the hidden concept)",
  "word_justification": "... (at least 35 words)",
  "confidence": 0.75}}"""
