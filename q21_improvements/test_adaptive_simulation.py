import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl")
)

from q21_improvements.mock_referee import MockReferee
from q21_improvements.scenarios import SCENARIO_1

def test_mock_referee_scores_document_id():
    referee = MockReferee(SCENARIO_1)
    
    guess = {"document_id": 1}
    score = referee.score_guess(guess)
    assert score["private_score"] == 100.0
    assert score["league_points"] == 3
    
    guess = {"document_id": 2}
    score = referee.score_guess(guess)
    assert score["private_score"] == 0.0
    assert score["league_points"] == 0

def test_mock_referee_returns_round_info():
    referee = MockReferee(SCENARIO_1)
    info = referee.get_round_start_info()
    assert "book_name" in info
    assert "book_hint" in info
