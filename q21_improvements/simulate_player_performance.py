# Area: Q21 Eval Pipeline — Baseline Measurement (pre-HyDE)
# PRD: q21_improvements/improvement_plan.md
"""
Offline evaluation harness for MyPlayerAI.

Usage (from project root):
    python q21_improvements/simulate_player_performance.py           # stub
    SIMULATE_REAL=1 python q21_improvements/simulate_player_performance.py  # real

KPIs: Win Rate, Word Accuracy, Information Density (Not Relevant count).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl")
)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

from q21_improvements.mock_referee import MockReferee
from q21_improvements.scenarios import ALL_SCENARIOS


# ── ANSI helpers ──────────────────────────────────────────────────

class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    CYAN = "\033[36m"; GREEN = "\033[92m"; RED = "\033[91m"
    YELLOW = "\033[33m"; WHITE = "\033[97m"


def _pass(label): return f"{C.GREEN}{C.BOLD}[PASS]{C.RESET} {label}"
def _fail(label): return f"{C.RED}{C.BOLD}[FAIL]{C.RESET} {label}"
def _bar(t): return f"\n{C.CYAN}{C.BOLD}{'━'*3} {t} {'━'*(56-len(t))}{C.RESET}"
def _trunc(s, n=60): return s[:n] + "…" if len(s) > n else s


# ── Stub player (no-API fallback) ────────────────────────────────

class _StubPlayer:
    """No-API stand-in for MyPlayerAI. Generic questions + naive guess."""

    def get_questions(self, ctx):
        book = ctx["dynamic"]["book_name"]
        aw = ctx["dynamic"].get("association_word", "theme")
        tiers = ["chapter topic"] * 7 + ["paragraph theme"] * 7 + ["specific words"] * 6
        return {"questions": [
            {"question_number": i, "question_text": f"About {tiers[i-1]} of '{book}'?",
             "options": {"A": f"Related to {aw}", "B": "Somewhat", "C": "Marginally", "D": "None"}}
            for i in range(1, 21)
        ]}

    def get_guess(self, ctx):
        aw = ctx["dynamic"].get("association_word", "theme")
        return {"opening_sentence": f"The book opens with a statement about {aw}.",
                "sentence_justification": " ".join(["analysis"] * 36),
                "associative_word": aw,
                "word_justification": " ".join(["reasoning"] * 36),
                "confidence": 0.3}


# ── Game runner ──────────────────────────────────────────────────

def run_game(scenario):
    """Run one simulated game. Set SIMULATE_REAL=1 for real MyPlayerAI."""
    referee = MockReferee(scenario)
    if os.getenv("SIMULATE_REAL", "0") == "1":
        from my_player import MyPlayerAI
        player = MyPlayerAI()
    else:
        player = _StubPlayer()

    round_info = referee.get_round_start_info()
    questions = player.get_questions({"dynamic": {**round_info}})["questions"]
    answers = referee.answer_questions(questions)
    nr = sum(1 for a in answers if a["answer"] == "Not Relevant")
    guess = player.get_guess({"dynamic": {**round_info, "answers": answers}})
    scores = referee.score_guess(guess)

    return {"name": scenario.get("name", scenario["book_name"]),
            "guessed": guess.get("opening_sentence", ""),
            "actual": scenario["opening_sentence"],
            "word_guessed": guess.get("associative_word", ""),
            "word_actual": scenario["actual_association_word"],
            "nr": nr, **scores}


# ── Reporting ────────────────────────────────────────────────────

def _print_result(r):
    print(_bar(r["name"]))
    print(f"  Guessed: {C.DIM}\"{_trunc(r['guessed'])}\"{C.RESET}")
    print(f"  Actual:  {C.DIM}\"{_trunc(r['actual'])}\"{C.RESET}")
    ss, ws, nr = r["opening_sentence_score"], r["word_score"], r["nr"]
    print(f"  {(_pass if ss >= 80 else _fail)(f'Sentence: {ss:.1f}%')}")
    print(f"  Word: {C.YELLOW}{r['word_guessed']}{C.RESET} vs {C.YELLOW}{r['word_actual']}{C.RESET}")
    print(f"  {(_pass if ws == 100 else _fail)(f'Word: {ws:.0f}%')}")
    print(f"  {(_pass if nr <= 5 else _fail)(f'Not Relevant: {nr}')}")
    print(f"  {C.WHITE}Score: {r['private_score']:.1f}  Points: {r['league_points']}{C.RESET}")


def _print_summary(results):
    n = len(results)
    wins = sum(1 for r in results if r["private_score"] >= 80)
    words = sum(1 for r in results if r["word_score"] == 100)
    avg_nr = sum(r["nr"] for r in results) / n
    print(_bar(f"AGGREGATE ({n} scenarios)"))
    print(f"  {(_pass if wins >= 2 else _fail)(f'Win Rate:     {wins}/{n} ({100*wins/n:.1f}%)')}")
    print(f"  {(_pass if words >= 2 else _fail)(f'Word Accuracy: {words}/{n} ({100*words/n:.1f}%)')}")
    print(f"  {(_pass if avg_nr <= 5 else _fail)(f'Avg NR:       {avg_nr:.1f}')}")
    print(f"  {C.WHITE}Avg Score: {sum(r['private_score'] for r in results)/n:.1f}{C.RESET}\n")


if __name__ == "__main__":
    import json
    print(f"\n{C.WHITE}{C.BOLD}Q21 Baseline Eval — {len(ALL_SCENARIOS)} scenarios{C.RESET}")
    results = [run_game(s) for s in ALL_SCENARIOS]
    for r in results:
        _print_result(r)
    _print_summary(results)
    out = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  {C.DIM}Results saved to {out}{C.RESET}")
