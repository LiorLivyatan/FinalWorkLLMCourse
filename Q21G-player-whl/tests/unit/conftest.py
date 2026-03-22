# Area: Player AI Testing
# PRD: docs/prd-player-ai.md
"""Unit-level conftest: auto-mock council and filter for player unit tests."""
import pytest


@pytest.fixture(autouse=True)
def mock_council_and_filter(mocker):
    """Mock council_deliberate, llm_filter, and deterministic_filter
    so player unit tests do not make real API calls to Gemini/OpenAI."""
    mocker.patch(
        "my_player.council_deliberate",
        return_value={
            "best_candidate_index": 0,
            "best_paragraph_text": "Mocked best paragraph text.",
            "gpt_vote": {"best_candidate_index": 0, "confidence": 8},
            "gemini_vote": {"best_candidate_index": 0, "confidence": 8},
        },
    )
    mocker.patch(
        "my_player.deterministic_filter",
        side_effect=lambda candidates, _enriched: candidates,
    )
    mocker.patch(
        "my_player.llm_filter",
        side_effect=lambda candidates, _enriched: candidates,
    )
