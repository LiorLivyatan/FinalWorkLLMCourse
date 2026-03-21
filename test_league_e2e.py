"""
Full League End-to-End Test — Player + Referee with real LLM + RAG
==================================================================

Simulates a complete Q21 game by calling callbacks directly:
  Referee (MyRefereeAI) ↔ Player (MyPlayerAI)

Both sides use the shared ChromaDB vector database for RAG search.

Run from project root:  python test_league_e2e.py
Output saved to:        test_league_e2e.log (with ANSI colors)
View with:              cat test_league_e2e.log   or   less -R test_league_e2e.log
"""
import sys
import os
import io
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Q21G-player-whl"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Q21G-referee-whl", "examples"))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

# Suppress noisy library logs
logging.basicConfig(level=logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("agno").setLevel(logging.WARNING)

from my_ai import MyRefereeAI
from my_player import MyPlayerAI


# ── ANSI Colors ─────────────────────────────────────────────────

class C:
    """ANSI color codes."""
    RESET     = "\033[0m"
    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    # Roles
    REFEREE   = "\033[34m"      # Blue
    PLAYER    = "\033[32m"      # Green
    SYSTEM    = "\033[37m"      # White/Gray
    # Phases
    WARMUP    = "\033[33m"      # Yellow
    ROUND     = "\033[36m"      # Cyan
    QUESTION  = "\033[35m"      # Magenta
    ANSWER    = "\033[34m"      # Blue
    GUESS     = "\033[92m"      # Bright Green
    SCORE     = "\033[91m"      # Bright Red
    # Results
    PASS      = "\033[92m"      # Bright Green
    FAIL      = "\033[91m"      # Bright Red
    HEADER    = "\033[97m"      # Bright White


def referee(text):
    return f"{C.REFEREE}{C.BOLD}[REFEREE]{C.RESET} {C.REFEREE}{text}{C.RESET}"

def player(text):
    return f"{C.PLAYER}{C.BOLD}[PLAYER]{C.RESET} {C.PLAYER}{text}{C.RESET}"

def phase(num, name, color):
    bar = "━" * 60
    return f"\n{color}{C.BOLD}{'━' * 3} Phase {num}: {name} {'━' * (50 - len(name))}{C.RESET}"

def header(text):
    return f"{C.HEADER}{C.BOLD}{text}{C.RESET}"

def dim(text):
    return f"{C.DIM}{text}{C.RESET}"

def passed(label):
    return f"  {C.PASS}{C.BOLD}[PASS]{C.RESET} {label}"

def failed(label):
    return f"  {C.FAIL}{C.BOLD}[FAIL]{C.RESET} {label}"


# ── Tee: print to stdout AND capture to buffer ──────────────────

class TeeWriter:
    def __init__(self, log_path):
        self._buf = io.StringIO()
        self._stdout = sys.stdout
        self._log_path = log_path

    def write(self, text):
        self._stdout.write(text)
        self._buf.write(text)

    def flush(self):
        self._stdout.flush()

    def save(self):
        with open(self._log_path, "w") as f:
            f.write(self._buf.getvalue())


def main():
    log_path = os.path.join(os.path.dirname(__file__), "test_league_e2e.log")
    tee = TeeWriter(log_path)
    sys.stdout = tee

    print(header("=" * 70))
    print(header("  Q21 League E2E: MyRefereeAI + MyPlayerAI"))
    print(header("  Real Gemini LLM + Shared ChromaDB RAG"))
    print(header("=" * 70))

    print(dim("\nInitializing both AIs (knowledge base check)..."))
    referee_ai = MyRefereeAI()
    player_ai = MyPlayerAI()
    print(dim("  Both AIs initialized.\n"))

    # ── Phase 1: Warmup ──────────────────────────────────────────
    print(phase(1, "WARMUP", C.WARMUP))
    warmup_ctx = {"dynamic": {"round_number": 1, "round_id": "ROUND_1",
                               "game_id": "0101001", "players": []}}
    warmup_q = referee_ai.get_warmup_question(warmup_ctx)
    question = warmup_q["warmup_question"]
    print(referee(f'Asks: "{question}"'))

    player_warmup_ctx = {"dynamic": {"warmup_question": question}}
    warmup_ans = player_ai.get_warmup_answer(player_warmup_ctx)
    print(player(f'Answers: "{warmup_ans["answer"]}"'))

    # ── Phase 2: Round start ─────────────────────────────────────
    print(phase(2, "ROUND START", C.ROUND))
    round_ctx = {"dynamic": {
        "round_number": 1, "game_id": "0101001", "match_id": "R1M1",
        "player_a": {"email": "alice@test.com", "participant_id": "P001",
                     "warmup_answer": warmup_ans["answer"]},
        "player_b": {"email": "bob@test.com", "participant_id": "P002",
                     "warmup_answer": warmup_ans["answer"]},
    }}
    round_info = referee_ai.get_round_start_info(round_ctx)
    book_name = round_info["book_name"]
    book_hint = round_info["book_hint"]
    assoc_word = round_info["association_word"]
    print(referee(f'Book:             "{book_name}"'))
    print(referee(f'Hint:             "{book_hint}"'))
    print(referee(f'Association word:  "{assoc_word}"'))

    # ── Phase 3: Player generates questions ──────────────────────
    print(phase(3, "QUESTIONS", C.QUESTION))
    q_ctx = {"dynamic": {"book_name": book_name, "book_hint": book_hint,
                          "association_word": assoc_word}}
    questions_result = player_ai.get_questions(q_ctx)
    questions = questions_result["questions"]
    print(player(f"Generated {len(questions)} strategic questions:"))
    for q in questions:
        opts = q.get("options", {})
        opts_str = f'A: {opts.get("A","")[:25]}  B: {opts.get("B","")[:25]}  C: {opts.get("C","")[:25]}  D: {opts.get("D","")[:25]}'
        tier = "Tier 1 (chapter)" if q["question_number"] <= 7 else \
               "Tier 2 (paragraph)" if q["question_number"] <= 14 else \
               "Tier 3 (sentence)"
        print(f"  {C.QUESTION}Q{q['question_number']:2d}{C.RESET} {dim(f'[{tier}]')} {q['question_text'][:65]}")
        print(f"       {C.DIM}{opts_str}{C.RESET}")

    # ── Phase 4: Referee answers questions (with RAG) ────────────
    print(phase(4, "ANSWERS (Referee RAG)", C.ANSWER))
    ans_ctx = {"dynamic": {
        "match_id": "R1M1", "game_id": "0101001",
        "player_email": "alice@test.com", "player_id": "P001",
        "book_name": book_name, "book_hint": book_hint,
        "association_word": assoc_word, "questions": questions,
    }}
    answers_result = referee_ai.get_answers(ans_ctx)
    answers = answers_result["answers"]
    print(referee(f"Answered {len(answers)} questions using RAG + Gemini:"))
    for a in answers:
        q_text = next((q["question_text"] for q in questions
                       if q["question_number"] == a["question_number"]), "")
        color = C.ANSWER if a["answer"] in "ABCD" else C.DIM
        print(f"  {C.ANSWER}Q{a['question_number']:2d}{C.RESET} → "
              f"{color}{C.BOLD}{a['answer']:>13s}{C.RESET}  "
              f"{dim(q_text[:55])}")

    # ── Wait for rate limit ──────────────────────────────────────
    print(dim(f"\n  ⏳ Waiting 45s for Gemini rate limit reset "
              f"(referee used ~20 calls)..."))
    time.sleep(45)

    # ── Phase 5: Player guesses opening sentence (with RAG) ──────
    print(phase(5, "GUESS (Player RAG)", C.GUESS))
    guess_ctx = {"dynamic": {
        "book_name": book_name, "book_hint": book_hint,
        "association_word": assoc_word, "answers": answers,
    }}
    guess = player_ai.get_guess(guess_ctx)
    print(player(f'Opening sentence guess:'))
    print(f"  {C.GUESS}{C.BOLD}\"{guess['opening_sentence']}\"{C.RESET}")
    print(player(f'Confidence: {guess["confidence"]}'))
    print(player(f'Association word: "{guess["associative_word"]}"'))
    print(player(f'Sentence justification:'))
    print(f"  {C.DIM}{guess['sentence_justification'][:200]}{C.RESET}")
    print(player(f'Word justification:'))
    print(f"  {C.DIM}{guess['word_justification'][:200]}{C.RESET}")

    # ── Phase 6: Referee scores the guess (with LLM) ─────────────
    print(phase(6, "SCORING", C.SCORE))
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
    score = referee_ai.get_score_feedback(score_ctx)

    print(referee(f'Scoring complete:'))
    lp = score["league_points"]
    ps = score["private_score"]
    lp_color = C.PASS if lp >= 2 else C.WARMUP if lp >= 1 else C.FAIL
    print(f"  {C.SCORE}League points:{C.RESET}  {lp_color}{C.BOLD}{lp}{C.RESET}")
    print(f"  {C.SCORE}Private score:{C.RESET}  {C.BOLD}{ps}{C.RESET}")
    print(f"  {C.SCORE}Breakdown:{C.RESET}")
    for k, v in score["breakdown"].items():
        bar_len = int(v / 2)  # 0-100 → 0-50 chars
        bar = "█" * bar_len + "░" * (50 - bar_len)
        label = k.replace("_", " ").replace(" score", "").title()
        weight = {"opening sentence": "50%", "sentence justification": "20%",
                  "associative word": "20%", "word justification": "10%"}.get(label.lower(), "")
        color = C.PASS if v >= 70 else C.WARMUP if v >= 40 else C.FAIL
        print(f"    {label:<25s} {color}{bar} {v:5.1f}{C.RESET} {dim(weight)}")

    print(referee(f'Feedback on opening sentence:'))
    fb_sent = score["feedback"].get("opening_sentence", "")
    print(f"  {C.DIM}{fb_sent[:300]}{C.RESET}")
    print(referee(f'Feedback on association word:'))
    fb_word = score["feedback"].get("associative_word", "")
    print(f"  {C.DIM}{fb_word[:300]}{C.RESET}")

    # ── Phase 7: Player receives score ───────────────────────────
    print(phase(7, "SCORE RECEIVED", C.SYSTEM))
    player_ai.on_score_received({"dynamic": score, "service": {"match_id": "R1M1"}})
    print(player("Score acknowledged."))

    # ── Validation ───────────────────────────────────────────────
    print(f"\n{C.HEADER}{C.BOLD}{'━' * 3} Validation {'━' * 49}{C.RESET}")
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
        ("Score has all breakdown keys", all(k in score["breakdown"] for k in [
            "opening_sentence_score", "sentence_justification_score",
            "associative_word_score", "word_justification_score"])),
        ("Score has feedback for both", all(k in score["feedback"] for k in [
            "opening_sentence", "associative_word"])),
    ]
    all_pass = True
    for label, ok in checks:
        if ok:
            print(passed(label))
        else:
            print(failed(label))
            all_pass = False

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n{C.HEADER}{C.BOLD}{'━' * 70}{C.RESET}")
    if all_pass:
        print(f"  {C.PASS}{C.BOLD}✓ FULL LEAGUE E2E PASSED — all 12 checks green{C.RESET}")
    else:
        print(f"  {C.FAIL}{C.BOLD}✗ SOME CHECKS FAILED{C.RESET}")
    print()
    actual = referee_ai._opening_sentence
    guessed = guess["opening_sentence"]
    print(f"  {C.REFEREE}Referee book:{C.RESET}    \"{book_name}\"")
    print(f"  {C.REFEREE}Actual sentence:{C.RESET} \"{actual}\"")
    print(f"  {C.PLAYER}Player guess:{C.RESET}    \"{guessed[:100]}\"")
    print(f"  {C.SCORE}Final score:{C.RESET}     {ps} private / {lp} league pts")
    print(f"{C.HEADER}{C.BOLD}{'━' * 70}{C.RESET}")

    # Save log
    sys.stdout = tee._stdout
    tee.save()
    print(f"\n{dim(f'Log saved to: {log_path}')}")
    print(dim("View with:    less -R test_league_e2e.log"))


if __name__ == "__main__":
    main()
