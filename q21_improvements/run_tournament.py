# Area: Q21 Eval Pipeline — Tournament Simulation
# PRD: docs/superpowers/specs/2026-03-23-tournament-simulation-design.md
"""MyPlayerAI vs parameterized MyRefereeAI tournament runner.

Usage (from project root):
    python q21_improvements/run_tournament.py
    python q21_improvements/run_tournament.py --dry-run
"""
import json
import os
import sys
import time
import argparse

# Player path MUST come first — its gemini_client has model/temperature params
# that council.py depends on. Referee's gemini_client is a simpler version.
_proj = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_proj, "Q21G-referee-whl", "examples"))
sys.path.insert(0, os.path.join(_proj, "Q21G-player-whl"))
sys.path.insert(0, _proj)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

from my_player import MyPlayerAI  # noqa: E402
from my_ai import MyRefereeAI     # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(__file__))
_SCENARIOS_PATH = os.path.join(_ROOT, "tournament_sim", "scenarios_generated.json")
_RESULTS_PATH   = os.path.join(_ROOT, "tournament_sim", "results.json")


# ── Scoring ──────────────────────────────────────────────────────────────────

def dual_score(private_score: float) -> dict:
    sdk  = 3 if private_score >= 80 else 2 if private_score >= 60 else 1 if private_score >= 40 else 0
    spec = 3 if private_score >= 85 else 2 if private_score >= 70 else 1 if private_score >= 50 else 0
    return {"sdk": sdk, "spec": spec}


# ── Game runner ──────────────────────────────────────────────────────────────

def run_game(scenario: dict, game_num: int) -> dict:
    referee    = MyRefereeAI(scenario)
    player     = MyPlayerAI()
    round_info = referee.get_round_start_info({"dynamic": {}})
    questions  = player.get_questions({"dynamic": {**round_info}})["questions"]
    answers    = referee.get_answers({"dynamic": {"questions": questions}})["answers"]
    guess      = player.get_guess({"dynamic": {**round_info, "answers": answers}})
    score      = referee.get_score_feedback({"dynamic": {"player_guess": {
        "opening_sentence":       guess.get("opening_sentence", ""),
        "sentence_justification": guess.get("sentence_justification", ""),
        "associative_word":       guess.get("associative_word", ""),
        "word_justification":     guess.get("word_justification", ""),
        "confidence":             guess.get("confidence", 0.5),
    }}})
    nr         = sum(1 for a in answers if a.get("answer") == "Not Relevant")
    sent_pct   = score.get("breakdown", {}).get("opening_sentence_score", 0.0)
    word_ok    = score.get("breakdown", {}).get("associative_word_score", 0.0) >= 80
    return {
        "game": game_num, "scenario_id": scenario["id"],
        "scenario_name": scenario.get("book_name", "?"),
        "guess": guess, "score": score, "nr": nr,
        "sent_pct": sent_pct, "word_correct": word_ok,
        "dual_scoring": dual_score(score["private_score"]),
    }


# ── Summary table ────────────────────────────────────────────────────────────

def print_summary(results: list) -> None:
    hdr = f"{'Game':<5} {'Scenario':<30} {'Sent%':>6} {'Word':>5} {'NR':>4} {'Score':>6} {'SDK':>4} {'Spec':>5}"
    print("\n" + hdr + "\n" + "-" * len(hdr))
    for r in results:
        if "error" in r:
            print(f"{r.get('game','?'):<5} ERROR: {r['error'][:55]}")
            continue
        print(f"{r['game']:<5} {r['scenario_name'][:29]:<30} "
              f"{r['sent_pct']:>5.1f}% {'YES' if r['word_correct'] else 'NO':>5} "
              f"{r['nr']:>4} {r['score']['private_score']:>6.1f} "
              f"{r['dual_scoring']['sdk']:>4} {r['dual_scoring']['spec']:>5}")
    good = [r for r in results if "error" not in r]
    if good:
        avg  = sum(r["score"]["private_score"] for r in good) / len(good)
        wins = sum(1 for r in good if r["dual_scoring"]["sdk"] == 3)
        print(f"\n  Played: {len(good)}/{len(results)}  Avg score: {avg:.1f}  SDK 3-pt wins: {wins}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Q21 Tournament Runner")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run only the first scenario")
    args = parser.parse_args()

    with open(_SCENARIOS_PATH, encoding="utf-8") as f:
        scenarios = json.load(f)

    if args.dry_run:
        scenarios = scenarios[:1]
        print("[dry-run] Running scenario 1 only")

    print(f"Running tournament: {len(scenarios)} scenario(s)\n")
    results = []

    for i, scenario in enumerate(scenarios, start=1):
        print(f"Game {i}/{len(scenarios)}: {scenario.get('book_name', '?')} ...", flush=True)
        try:
            result = run_game(scenario, i)
            results.append(result)
            ps = result["score"]["private_score"]
            ds = result["dual_scoring"]
            print(f"  -> score={ps:.1f}  sdk={ds['sdk']}  spec={ds['spec']}")
        except Exception as e:
            print(f"  Game {i} failed: {e}")
            results.append({"game": i, "scenario_id": scenario["id"], "error": str(e)})

        if i < len(scenarios):
            time.sleep(5)

    print_summary(results)

    os.makedirs(os.path.dirname(_RESULTS_PATH), exist_ok=True)
    with open(_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved -> {_RESULTS_PATH}")


if __name__ == "__main__":
    main()
