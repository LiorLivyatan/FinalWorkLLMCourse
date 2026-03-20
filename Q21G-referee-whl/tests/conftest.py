# Area: Student Callbacks
# PRD: docs/superpowers/specs/2026-03-20-student-referee-ai-design.md
"""Session-scoped patch so gemini_client can be imported without a real API key."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure examples/ is on the path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

# Set a fake key so genai.Client() doesn't raise at import time
os.environ.setdefault("GOOGLE_API_KEY", "fake-key-for-tests")

# Patch google.genai.Client before gemini_client is imported
_mock_client = MagicMock()
_mock_response = MagicMock()
_mock_response.text = "A"
_mock_client.models.generate_content.return_value = _mock_response

_patcher = patch("google.genai.Client", return_value=_mock_client)
_patcher.start()
