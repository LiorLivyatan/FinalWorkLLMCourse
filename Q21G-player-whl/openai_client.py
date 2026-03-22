# Area: Player AI - LLM Client
# PRD: docs/prd-player-ai.md
"""Thin wrapper around OpenAI SDK for text generation.

Uses OPENAI_API_KEY (auto-detected by SDK) and OPENAI_MODEL env var.
Exposes two functions: generate() for raw text, generate_json() for
parsed JSON responses with structured output.
"""
import json
import os

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_client = OpenAI()
_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def generate(prompt: str) -> str:
    """Generate text from a prompt."""
    response = _client.chat.completions.create(
        model=_DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_json(prompt: str) -> dict:
    """Generate a JSON response from a prompt."""
    response = _client.chat.completions.create(
        model=_DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        return {}
