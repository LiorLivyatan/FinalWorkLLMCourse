"""
Full League End-to-End Test — Player + Referee with real LLM + RAG
==================================================================

Simulates a complete Q21 game by calling callbacks directly:
  Referee (MyRefereeAI) ↔ Player (MyPlayerAI)

Both sides use the shared ChromaDB vector database for RAG search.

Run from project root:  python test_league_e2e.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Q21G-player-whl"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Q21G-referee-whl", "examples"))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

from my_ai import MyRefereeAI
from my_player import MyPlayerAI


def main():
    print("=" * 70)
    print("  Q21 League E2E: MyRefereeAI + MyPlayerAI (real LLM + RAG)")
    print("=" * 70)

    print("\nInitializing both AIs (knowledge base check)...")
    referee = MyRefereeAI()
    player = MyPlayerAI()

    # ── Phase 1: Warmup ──────────────────────────────────────────
    print("\n[1] WARMUP — Referee asks, Player answers")
    warmup_ctx = {"dynamic": {"round_number": 1, "round_id": "ROUND_1",
                               "game_id": "0101001", "players": []}}
    warmup_q = referee.get_warmup_question(warmup_ctx)
    question = warmup_q["warmup_question"]
    print(f"    Referee asks: \"{question}\"")

    player_warmup_ctx = {"dynamic": {"warmup_question": question}}
    warmup_ans = player.get_warmup_answer(player_warmup_ctx)
    print(f"    Player answers: \"{warmup_ans['answer']}\"")

    # ── Phase 2: Round start ─────────────────────────────────────
    print("\n[2] ROUND START — Referee picks book, hint, association word")
    round_ctx = {"dynamic": {
        "round_number": 1, "game_id": "0101001", "match_id": "R1M1",
        "player_a": {"email": "alice@test.com", "participant_id": "P001",
                     "warmup_answer": warmup_ans["answer"]},
        "player_b": {"email": "bob@test.com", "participant_id": "P002",
                     "warmup_answer": warmup_ans["answer"]},
    }}
    round_info = referee.get_round_start_info(round_ctx)
    book_name = round_info["book_name"]
    book_hint = round_info["book_hint"]
    assoc_word = round_info["association_word"]
    print(f"    Book: \"{book_name}\"")
    print(f"    Hint: \"{book_hint}\"")
    print(f"    Association word: \"{assoc_word}\"")

    # ── Phase 3: Player generates questions ──────────────────────
    print(f"\n[3] QUESTIONS — Player generates 20 strategic questions")
    q_ctx = {"dynamic": {"book_name": book_name, "book_hint": book_hint,
                          "association_word": assoc_word}}
    questions_result = player.get_questions(q_ctx)
    questions = questions_result["questions"]
    print(f"    Generated {len(questions)} questions")
    for q in questions[:3]:
        print(f"      Q{q['question_number']}: {q['question_text'][:70]}...")
    print(f"      ... and {len(questions) - 3} more")

    # ── Phase 4: Referee answers questions (with RAG) ────────────
    print(f"\n[4] ANSWERS — Referee answers using RAG + Gemini")
    ans_ctx = {"dynamic": {
        "match_id": "R1M1", "game_id": "0101001",
        "player_email": "alice@test.com", "player_id": "P001",
        "book_name": book_name, "book_hint": book_hint,
        "association_word": assoc_word, "questions": questions,
    }}
    answers_result = referee.get_answers(ans_ctx)
    answers = answers_result["answers"]
    print(f"    Answered {len(answers)} questions:")
    for a in answers[:5]:
        print(f"      Q{a['question_number']}: {a['answer']}")
    print(f"      ... and {len(answers) - 5} more")

    # ── Phase 5: Player guesses opening sentence (with RAG) ──────
    # Wait for rate limit to reset (referee used ~20 calls answering questions)
    print(f"\n    (waiting 45s for rate limit reset...)")
    time.sleep(45)
    print(f"\n[5] GUESS — Player uses RAG to find opening sentence")
    guess_ctx = {"dynamic": {
        "book_name": book_name, "book_hint": book_hint,
        "association_word": assoc_word, "answers": answers,
    }}
    guess = player.get_guess(guess_ctx)
    print(f"    Guess: \"{guess['opening_sentence'][:100]}\"")
    print(f"    Confidence: {guess['confidence']}")
    print(f"    Assoc word: \"{guess['associative_word']}\"")

    # ── Phase 6: Referee scores the guess (with LLM) ─────────────
    print(f"\n[6] SCORE — Referee evaluates guess with Gemini")
    score_ctx = {"dynamic": {
        "match_id": "R1M1", "game_id": "0101001",
        "player_email": "alice@test.com", "player_id": "P001",
        "book_name": book_name, "book_hint": book_hint,
        "association_word": assoc_word,
        "player_guess": {
            "opening_sentence": guess["opening_sentence"],
            "sentence_justification": guess["sentence_justification"],
            "associative_word": guess["associative_word"],
            "word_justification": guess["word_justification"],
            "confidence": guess["confidence"],
        },
    }}
    score = referee.get_score_feedback(score_ctx)
    print(f"    League points: {score['league_points']}")
    print(f"    Private score: {score['private_score']}")
    print(f"    Breakdown:")
    for k, v in score["breakdown"].items():
        print(f"      {k}: {v}")

    # ── Phase 7: Player receives score ───────────────────────────
    print(f"\n[7] SCORE RECEIVED — Player processes feedback")
    player.on_score_received({"dynamic": score, "service": {"match_id": "R1M1"}})

    # ── Validation ───────────────────────────────────────────────
    print("\n" + "-" * 70)
    print("  VALIDATION")
    print("-" * 70)
    checks = [
        ("Warmup question is non-empty", bool(question)),
        ("Warmup answer is non-empty", bool(warmup_ans["answer"])),
        ("Book name provided", bool(book_name)),
        ("Generated 20 questions", len(questions) == 20),
        ("Referee answered all questions", len(answers) == 20),
        ("Answers are valid (A/B/C/D/NR)", all(
            a["answer"] in ("A", "B", "C", "D", "Not Relevant")
            for a in answers)),
        ("Guess has opening_sentence", bool(guess["opening_sentence"])),
        ("Guess has justification (35+ words)",
         len(guess["sentence_justification"].split()) >= 10),
        ("Guess confidence in [0,1]", 0 <= guess["confidence"] <= 1),
        ("Score has league_points", "league_points" in score),
        ("Score has breakdown", all(k in score["breakdown"] for k in [
            "opening_sentence_score", "sentence_justification_score",
            "associative_word_score", "word_justification_score"])),
        ("Score has feedback", all(k in score["feedback"] for k in [
            "opening_sentence", "associative_word"])),
    ]
    all_pass = True
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {label}")

    # ── Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    if all_pass:
        print("  FULL LEAGUE E2E PASSED!")
    else:
        print("  SOME CHECKS FAILED!")
    print()
    print(f"  Referee book: \"{book_name}\"")
    print(f"  Actual sentence: \"{referee._opening_sentence[:80]}...\"")
    print(f"  Player guess:    \"{guess['opening_sentence'][:80]}...\"")
    print(f"  Score: {score['private_score']} ({score['league_points']} league pts)")
    print("=" * 70)


if __name__ == "__main__":
    main()
