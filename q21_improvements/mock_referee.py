# Area: Q21 Eval Pipeline
# PRD: q21_improvements/adaptive_simulation_plan.md
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))
from gemini_client import generate

class MockReferee:
    """LLM-based referee backed by a ground-truth scenario dict."""

    def __init__(self, scenario: dict):
        self.scenario = scenario

    def get_round_start_info(self) -> dict:
        return {
            "book_name": self.scenario["book_name"],
            "book_hint": self.scenario["book_hint"],
        }

    def answer_question(self, question: str) -> str:
        """
        Answer a binary question using an LLM. 
        Prompts the LLM with the scenario's full text.
        """
        prompt = f"""You are the Game Judge in a 20-Questions deductive reasoning game.
Your task is to answer a Player's Yes/No question based ONLY on the following Ground Truth Text.

Ground Truth Text:
{self.scenario.get("full_text", self.scenario["opening_sentence"])}

Player's Question: {question}

You must answer accurately. If the question cannot be answered from the text, reply 'Not Relevant'.
Provide NO reasoning, NO explanation. 
Your response must be exactly one of these three options: Yes, No, or Not Relevant.
"""
        response = generate(prompt).strip()
        
        answer = "Not Relevant"
        for valid in ["Yes", "No", "Not Relevant"]:
            if valid.lower() in response.lower():
                answer = valid
                break
        return answer

    def score_guess(self, guess: dict) -> dict:
        """Score based on guessing the correct document_id."""
        actual_id = self.scenario.get("document_id")
        try:
            guessed_id = int(guess.get("document_id", -1))
        except (ValueError, TypeError):
            guessed_id = -1
        
        if actual_id == guessed_id:
            private = 100.0
        else:
            private = 0.0

        league_points = 3 if private == 100.0 else 0

        return {
            "private_score": private,
            "league_points": league_points,
        }
