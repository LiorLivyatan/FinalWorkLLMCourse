# Area: Player AI - Deliberation & Guess Prompt Builders
# PRD: docs/prd-player-ai.md
"""Deliberation and guess prompt builders for MyPlayerAI."""


def format_answer(a: dict) -> str:
    """Format a single Q&A pair, resolving the answer letter to option text."""
    qnum = a["question_number"]
    q_text = a.get("question_text", "")
    letter = a["answer"]
    opts = a.get("options", {})
    selected = opts.get(letter, letter)  # resolve "B" → actual option text
    if q_text:
        return f"Q{qnum}: {q_text} → {selected}"
    return f"Q{qnum}: → {selected}"


def build_deliberation_prompt(
    book_name: str, answers: list[dict], candidates_text: str,
) -> str:
    """Score each candidate paragraph against the referee's answers.

    Candidates are likely in Hebrew — the prompt handles both languages.
    """
    answers_str = "\n".join(format_answer(a) for a in answers)
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


def build_council_prompt(
    candidates: list[dict], enriched_answers: list[dict],
) -> str:
    """Council deliberation prompt for comparing 2-3 candidates."""
    answers_str = "\n".join(format_answer(a) for a in enriched_answers)
    cands_str = "\n\n---\n\n".join(
        f"Candidate {i}:\n{c['content']}"
        for i, c in enumerate(candidates)
    )
    return f"""You are one member of a deliberation council. Compare these
candidate paragraphs and determine which is the target paragraph.

Evidence from 20 Q&A questions:
{answers_str}

Candidates:
{cands_str}

For each candidate evaluate:
1. Does the FORMAT match the Q&A evidence? (list vs prose vs code)
2. Does the CONTENT match the Q&A evidence? (topic, entities, domain)
3. Does it contain the structural features the answers describe?

Pick the single best match. Score your confidence 1-10 (10 = certain).

Reply with ONLY valid JSON:
{{"best_candidate_index": 0, "confidence": 8, "reasoning": "..."}}"""


def build_guess_prompt(
    book_name: str, book_hint: str, association_word: str,
    answers: list[dict], candidates_text: str,
) -> str:
    """Final guess extraction — handles Hebrew source, English output."""
    answers_str = "\n".join(format_answer(a) for a in answers)
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
2. DO NOT translate the sentence. Extract the exact verbatim Hebrew string from the source text. The "opening_sentence" in your JSON response must be the original authentic Hebrew.
3. Do NOT copy section numbers, table headers, or labels — only the first actual content sentence.
4. For "associative_word": what HIDDEN CONCEPT connects "{association_word}"
   to the paragraph's core thesis? This is NOT "{association_word}" itself.
   Think about the underlying mechanism or principle.

Reply with ONLY valid JSON:
{{"opening_sentence": "... (first sentence, in ENGLISH)",
  "sentence_justification": "... (at least 35 words explaining your reasoning)",
  "associative_word": "... (one English word — the hidden concept)",
  "word_justification": "... (at least 35 words explaining your choice)",
  "confidence": 0.75}}"""
