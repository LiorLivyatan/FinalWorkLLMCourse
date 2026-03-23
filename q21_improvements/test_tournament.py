# Area: Q21 Eval Pipeline — Tournament Simulation
# PRD: docs/superpowers/specs/2026-03-23-tournament-simulation-design.md
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))


def test_hint_has_no_paragraph_words():
    from q21_improvements.generate_scenarios import validate_hint
    paragraph = "מגבלת150שורות לקובץ היא לא מספר שרירותי."
    good_hint = "architectural constraint reflecting cognitive load thresholds"
    bad_hint = "מגבלת שורות לקובץ coding rule"
    assert validate_hint(good_hint, paragraph) == True
    assert validate_hint(bad_hint, paragraph) == False


def test_hint_word_count():
    from q21_improvements.generate_scenarios import validate_hint
    short = "a b c"
    long = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"
    assert validate_hint(short, "irrelevant") == True
    assert validate_hint(long, "irrelevant") == False
