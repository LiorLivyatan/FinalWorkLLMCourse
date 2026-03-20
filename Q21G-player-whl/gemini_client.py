# Area: Player AI - LLM Client
# PRD: docs/prd-player-ai.md
"""Thin wrapper around Google GenAI SDK for text generation.

Uses GEMINI_MODEL and GOOGLE_API_KEY environment variables.
Exposes two functions: generate() for raw text, generate_json()
for parsed JSON responses.
"""
import json
import os
import re

from google import genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY", ""))
_DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"


def generate(prompt: str) -> str:
    """Generate text from a prompt using Gemini.

    Args:
        prompt: The full prompt to send to Gemini.

    Returns:
        The model's text response.
    """
    model_id = os.getenv("GEMINI_MODEL", _DEFAULT_MODEL)
    response = _client.models.generate_content(
        model=model_id, contents=prompt,
    )
    return response.text


def generate_json(prompt: str) -> dict:
    """Generate a JSON response from a prompt.

    Handles markdown code blocks and returns {} on parse failure.
    """
    raw = generate(prompt)
    return _parse_json(raw)


def _parse_json(text: str) -> dict:
    """Extract and parse JSON from text, handling code blocks."""
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return {}
