# Area: Player AI
# PRD: docs/prd-player-ai.md
"""Unit tests for MyPlayerAI methods."""
import json
import pytest
from unittest.mock import MagicMock, patch


def _make_player(mocker):
    """Create a MyPlayerAI with mocked dependencies."""
    mocker.patch("my_player.ensure_indexed")
    mocker.patch("my_player.search", return_value=[
        {"content": "Multi-agent systems are composed of multiple interacting agents."},
        {"content": "Agents communicate through message passing protocols."},
    ])
    from my_player import MyPlayerAI
    return MyPlayerAI()


class TestGetWarmupAnswer:
    def test_returns_dict_with_answer_key(self, mocker, sample_ctx_warmup):
        mocker.patch("my_player.generate", return_value="42")
        player = _make_player(mocker)
        result = player.get_warmup_answer(sample_ctx_warmup)
        assert isinstance(result, dict)
        assert "answer" in result

    def test_answer_is_string(self, mocker, sample_ctx_warmup):
        mocker.patch("my_player.generate", return_value="42")
        player = _make_player(mocker)
        result = player.get_warmup_answer(sample_ctx_warmup)
        assert isinstance(result["answer"], str)

    def test_passes_question_to_llm(self, mocker, sample_ctx_warmup):
        mock_gen = mocker.patch("my_player.generate", return_value="42")
        player = _make_player(mocker)
        player.get_warmup_answer(sample_ctx_warmup)
        call_args = mock_gen.call_args[0][0]
        assert "6 * 7" in call_args


class TestGetQuestions:
    def _mock_questions_response(self):
        """Return a valid 20-question JSON string."""
        questions = []
        for i in range(1, 21):
            questions.append({
                "question_number": i,
                "question_text": f"Is this about topic {i}?",
                "options": {"A": "Yes", "B": "No", "C": "Partially", "D": "Unknown"},
            })
        return json.dumps({"questions": questions})

    def test_returns_exactly_20_questions(self, mocker, sample_ctx_questions):
        mocker.patch(
            "my_player.generate_json",
            return_value=json.loads(self._mock_questions_response()),
        )
        player = _make_player(mocker)
        result = player.get_questions(sample_ctx_questions)
        assert "questions" in result
        assert len(result["questions"]) == 20

    def test_each_question_has_required_fields(self, mocker, sample_ctx_questions):
        mocker.patch(
            "my_player.generate_json",
            return_value=json.loads(self._mock_questions_response()),
        )
        player = _make_player(mocker)
        result = player.get_questions(sample_ctx_questions)
        for q in result["questions"]:
            assert "question_number" in q
            assert "question_text" in q
            assert "options" in q
            assert set(q["options"].keys()) == {"A", "B", "C", "D"}

    def test_question_numbers_are_sequential(self, mocker, sample_ctx_questions):
        mocker.patch(
            "my_player.generate_json",
            return_value=json.loads(self._mock_questions_response()),
        )
        player = _make_player(mocker)
        result = player.get_questions(sample_ctx_questions)
        numbers = [q["question_number"] for q in result["questions"]]
        assert numbers == list(range(1, 21))


class TestGetGuess:
    def _mock_guess_response(self):
        return {
            "opening_sentence": "Multi-agent systems are composed of agents.",
            "sentence_justification": (
                "Based on the answers received to the twenty questions, "
                "the pattern of responses strongly suggests this is a chapter "
                "about multi-agent systems and their composition as autonomous "
                "entities that interact within shared environments and coordinate "
                "their behaviors toward common goals."
            ),
            "associative_word": "cooperation",
            "word_justification": (
                "The word cooperation captures the essential core theme of "
                "multi-agent interaction where agents work together toward "
                "shared goals in a distributed environment requiring careful "
                "coordination and communication between all of the participating "
                "autonomous entities involved."
            ),
            "confidence": 0.75,
        }

    def test_has_all_required_fields(self, mocker, sample_ctx_guess):
        mocker.patch("my_player.generate_json", return_value=self._mock_guess_response())
        player = _make_player(mocker)
        result = player.get_guess(sample_ctx_guess)
        assert "opening_sentence" in result
        assert "sentence_justification" in result
        assert "associative_word" in result
        assert "word_justification" in result
        assert "confidence" in result

    def test_confidence_is_float_in_range(self, mocker, sample_ctx_guess):
        mocker.patch("my_player.generate_json", return_value=self._mock_guess_response())
        player = _make_player(mocker)
        result = player.get_guess(sample_ctx_guess)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_justifications_have_minimum_words(self, mocker, sample_ctx_guess):
        mocker.patch("my_player.generate_json", return_value=self._mock_guess_response())
        player = _make_player(mocker)
        result = player.get_guess(sample_ctx_guess)
        assert len(result["sentence_justification"].split()) >= 35
        assert len(result["word_justification"].split()) >= 35

    def test_calls_search_with_book_info(self, mocker, sample_ctx_guess):
        mocker.patch("my_player.generate_json", return_value=self._mock_guess_response())
        mock_search = mocker.patch("my_player.search", return_value=[
            {"content": "Some paragraph text."},
        ])
        mocker.patch("my_player.ensure_indexed")
        from my_player import MyPlayerAI
        player = MyPlayerAI()
        player.get_guess(sample_ctx_guess)
        mock_search.assert_called_once()


class TestOnScoreReceived:
    def test_does_not_raise(self, mocker, sample_ctx_score):
        player = _make_player(mocker)
        player.on_score_received(sample_ctx_score)
