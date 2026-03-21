# Area: Q21 Eval Pipeline
# PRD: q21_improvements/adaptive_simulation_plan.md
"""
Interactive offline evaluation harness for MyPlayerAI.
Simulates a real 20-Questions game turn-by-turn.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl")
)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

from q21_improvements.mock_referee import MockReferee
from q21_improvements.scenarios import ALL_SCENARIOS
from my_player import MyPlayerAI

class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    CYAN = "\033[36m"; GREEN = "\033[92m"; RED = "\033[91m"
    YELLOW = "\033[33m"; WHITE = "\033[97m"

def run_adaptive_game(scenario):
    referee = MockReferee(scenario)
    player = MyPlayerAI()
    
    round_info = referee.get_round_start_info()
    book_name = round_info["book_name"]
    book_hint = round_info["book_hint"]
    
    history = []
    
    print(f"\n{C.CYAN}{C.BOLD}━━━ Scenario: {scenario['name']} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
    print(f"{C.DIM}Hint: {book_hint}{C.RESET}")
    
    nr_count = 0
    for turn in range(1, 21):
        ctx = {"dynamic": {"history": history, "book_hint": book_hint}}
        question_response = player.get_next_question(ctx)
        question = question_response.get("question", "")
        
        answer = referee.answer_question(question)
        if answer == "Not Relevant":
            nr_count += 1
            
        print(f"  {C.BOLD}Q{turn}:{C.RESET} {question}")
        color = C.GREEN if answer == "Yes" else C.RED if answer == "No" else C.YELLOW
        print(f"  {C.BOLD}A{turn}:{C.RESET} {color}{answer}{C.RESET}\n")
        
        history.append({"question": question, "answer": answer})
        
    ctx = {"dynamic": {"history": history}}
    final_guess = player.get_final_guess(ctx)
    scores = referee.score_guess(final_guess)
    
    actual_id = scenario.get("document_id")
    guessed_id = final_guess.get("document_id")
    
    win = (actual_id == guessed_id)
    print(f"  Guessed ID: {guessed_id} | Actual ID: {actual_id}")
    print(f"  {C.GREEN if win else C.RED}Score: {scores['private_score']} Points: {scores['league_points']}{C.RESET}")
    print(f"  Not Relevant count: {nr_count}")
    
    return {
        "name": scenario["name"],
        "actual_id": actual_id,
        "guessed_id": guessed_id,
        "win": win,
        "nr_count": nr_count,
        **scores
    }

if __name__ == "__main__":
    print(f"\n{C.WHITE}{C.BOLD}Q21 Adaptive Eval — {len(ALL_SCENARIOS)} scenarios{C.RESET}")
    results = [run_adaptive_game(s) for s in ALL_SCENARIOS]
    
    n = len(results)
    wins = sum(1 for r in results if r["win"])
    avg_nr = sum(r["nr_count"] for r in results) / n
    print(f"\n{C.CYAN}{C.BOLD}━━━ AGGREGATE ({n} scenarios) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
    print(f"  Win Rate:     {wins}/{n} ({100*wins/n:.1f}%)")
    print(f"  Avg NR:       {avg_nr:.1f}")
    
    out = os.path.join(os.path.dirname(__file__), "adaptive_eval_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  {C.DIM}Results saved to {out}{C.RESET}")
