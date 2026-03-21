"""End-to-end game simulation through GameExecutor + MyPlayerAI.

Runs the full game flow with real Gemini inference and RAG search:
  1. Warmup  — answer a math question
  2. Questions — generate 20 strategic questions about a course chapter
  3. Guess — use RAG to find the opening sentence
  4. Score — receive and process score feedback
"""
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

from my_player import MyPlayerAI
from _infra.gmc.game_executor import GameExecutor


def main():
    print("Initializing MyPlayerAI (indexing check)...")
    player = MyPlayerAI()
    executor = GameExecutor(player_ai=player)

    # ── Phase 1: Warmup ──────────────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 1: WARMUP")
    print("=" * 60)
    warmup_result = executor.execute_warmup({
        "match_id": "0101001",
        "warmup_question": "What is 17 * 3 + 9?",
    })
    print(f"Question: {warmup_result['warmup_question']}")
    print(f"Answer:   {warmup_result['warmup_answer']}")

    # ── Phase 2: Questions ───────────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 2: GENERATE 20 QUESTIONS")
    print("=" * 60)
    round_payload = {
        "match_id": "0101001",
        "book_name": "AI Agents with Model Context Protocol",
        "book_hint": "Architecture for connecting AI models to external tools and data sources",
        "association_word": "protocol",
    }
    questions_result = executor.execute_questions(round_payload)
    questions = questions_result["questions"]
    print(f"Generated {len(questions)} questions")
    for q in questions[:3]:
        print(f"  Q{q['question_number']}: {q['question_text'][:80]}...")
    if len(questions) > 3:
        print(f"  ... and {len(questions) - 3} more")

    # ── Phase 3: Guess (with RAG) ────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 3: GUESS (RAG search + Gemini inference)")
    print("=" * 60)
    # Simulate answers the referee would send back
    fake_answers = [
        {"question_number": i, "answer": ["A", "B", "C", "D"][i % 4]}
        for i in range(1, 21)
    ]
    guess_payload = {
        **round_payload,
        "answers": fake_answers,
    }
    guess_result = executor.execute_guess(guess_payload)
    guess = guess_result["guess"]
    print(f"Opening sentence: {guess['opening_sentence'][:120]}...")
    print(f"Confidence:       {guess['confidence']}")
    print(f"Assoc. word:      {guess['associative_word']}")
    print(f"Sent. justif.:    {guess['sentence_justification'][:120]}...")
    print(f"Word justif.:     {guess['word_justification'][:120]}...")

    # ── Phase 4: Score ───────────────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 4: SCORE FEEDBACK")
    print("=" * 60)
    score_result = executor.handle_score({
        "match_id": "0101001",
        "league_points": 2,
        "private_score": 65.0,
        "breakdown": {
            "opening_sentence_score": 70.0,
            "sentence_justification_score": 60.0,
            "associative_word_score": 65.0,
            "word_justification_score": 55.0,
        },
    })
    print(f"League points:  {score_result['league_points']}")
    print(f"Private score:  {score_result['private_score']}")

    # ── Validation ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)
    checks = [
        ("Warmup answer is numeric", warmup_result["warmup_answer"].strip().replace(".", "").isdigit()),
        ("Generated exactly 20 questions", len(questions) == 20),
        ("Questions have required fields", all(
            "question_number" in q and "question_text" in q and "options" in q
            for q in questions
        )),
        ("Guess has opening_sentence", bool(guess["opening_sentence"])),
        ("Guess has sentence_justification", len(guess["sentence_justification"].split()) >= 10),
        ("Guess has associative_word", bool(guess["associative_word"])),
        ("Guess confidence in range", 0.0 <= guess["confidence"] <= 1.0),
        ("Score processed successfully", score_result["league_points"] == 2),
    ]
    all_pass = True
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {label}")

    print(f"\n{'All checks passed!' if all_pass else 'Some checks FAILED.'}")


if __name__ == "__main__":
    main()
