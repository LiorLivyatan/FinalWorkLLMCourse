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


def generate(prompt: str, model: str = None, temperature: float = 0.0) -> str:
    """Generate text. Default temperature=0 for deterministic output."""
    from google.genai.types import GenerateContentConfig
    model_id = model or os.getenv("GEMINI_MODEL", _DEFAULT_MODEL)
    response = _client.models.generate_content(
        model=model_id, contents=prompt,
        config=GenerateContentConfig(temperature=temperature),
    )
    return response.text


def generate_json(prompt: str, model: str = None,
                  temperature: float = 0.0) -> dict:
    """Generate JSON. Handles code blocks. Returns {} on failure."""
    raw = generate(prompt, model=model, temperature=temperature)
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
