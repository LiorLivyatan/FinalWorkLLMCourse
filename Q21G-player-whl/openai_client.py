# Area: Player AI - LLM Client
# PRD: docs/prd-player-ai.md
"""Thin wrapper around OpenAI SDK for text generation.

Uses OPENAI_API_KEY (auto-detected by SDK) and OPENAI_MODEL env var.
Supports per-call temperature override for deterministic vs creative tasks.
"""
import json
import os

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_client = OpenAI()
_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def generate(prompt: str, temperature: float = 0.0) -> str:
    """Generate text. Default temperature=0 for deterministic output."""
    response = _client.chat.completions.create(
        model=_DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content


def generate_json(prompt: str, temperature: float = 0.0) -> dict:
    """Generate JSON. Default temperature=0 for deterministic output."""
    response = _client.chat.completions.create(
        model=_DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        return {}
