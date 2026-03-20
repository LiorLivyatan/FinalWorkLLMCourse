# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Tests for book_config constants."""
import importlib.util
import pathlib


def load_book_config():
    spec = importlib.util.spec_from_file_location(
        "book_config",
        pathlib.Path(__file__).parent.parent / "examples" / "book_config.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_all_constants_non_empty():
    mod = load_book_config()
    for attr in ["BOOK_NAME", "BOOK_HINT", "ASSOCIATION_WORD",
                 "ACTUAL_ASSOCIATION_WORD", "OPENING_SENTENCE"]:
        val = getattr(mod, attr)
        assert isinstance(val, str) and len(val) > 0, f"{attr} is empty"


def test_hint_within_15_words():
    mod = load_book_config()
    assert len(mod.BOOK_HINT.split()) <= 15


def test_association_word_differs_from_actual():
    mod = load_book_config()
    assert mod.ASSOCIATION_WORD != mod.ACTUAL_ASSOCIATION_WORD


def test_opening_sentence_ends_with_period():
    mod = load_book_config()
    assert mod.OPENING_SENTENCE.endswith(".")
