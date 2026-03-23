# Area: Q21 Eval Pipeline — Tournament Simulation
# PRD: docs/superpowers/specs/2026-03-23-tournament-simulation-design.md
"""Randomly generates 10 referee scenarios from ChromaDB course material.

Connects to the pre-built ChromaDB at ./database, picks random chunks,
calls Gemini Flash to create game metadata, validates hints, and saves
the result to tournament_sim/scenarios_generated.json.

Usage (from project root):
    python q21_improvements/generate_scenarios.py
"""
import json
import os
import random
import re
import sys

import chromadb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))
from gemini_client import generate_json  # noqa: E402

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
_OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tournament_sim", "scenarios_generated.json")
_NUM_SCENARIOS = 10
_MAX_RETRIES = 3

_HE_STOP_WORDS = {"של", "את", "על", "עם", "הם", "היא", "הוא", "זה", "זו",
                  "כי", "אם", "לא", "גם", "כל", "בין", "אחד", "יש", "אין"}

_REFEREE_PROMPT = """\
You are a Q21 League referee. Given this Hebrew paragraph from a university textbook, generate game metadata.

Paragraph:
{chunk_text}

Rules:
1. book_name: creative title, up to 5 words
2. book_hint: up to 15 words, NO WORDS from the paragraph (this is critical)
3. association_word: the CATEGORY shown to players (e.g., "memory", "limits")
4. actual_association_word: the SECRET specific concept players must guess
5. opening_sentence: the EXACT verbatim first sentence from the paragraph
6. warmup_question: a simple math problem (e.g., "What is 8 * 7?")

Reply with ONLY valid JSON."""


def validate_hint(hint: str, paragraph: str) -> bool:
    """Return True if hint has ≤15 words and shares no content words with paragraph.

    Hebrew stop words (של, את, על, ...) are ignored during overlap check.
    """
    hint_words = hint.split()
    if len(hint_words) > 15:
        return False
    para_tokens = set(re.split(r"\s+", paragraph.lower())) - _HE_STOP_WORDS
    for word in hint_words:
        if word.lower() in para_tokens:
            return False
    return True


def _extract_opening_sentence(text: str) -> str:
    """Return the first sentence from a chunk of text."""
    for sep in (".", "!", "?", "\n"):
        idx = text.find(sep)
        if idx != -1:
            return text[: idx + 1].strip()
    return text.strip()


def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=_DB_PATH)
    return client.get_collection("course_material")


def _fetch_random_chunk(col: chromadb.Collection) -> dict:
    count = col.count()
    offset = random.randint(0, count - 1)
    result = col.get(offset=offset, limit=1)
    return {
        "text": result["documents"][0],
        "metadata": result["metadatas"][0],
    }


def _generate_metadata(chunk_text: str) -> dict:
    prompt = _REFEREE_PROMPT.format(chunk_text=chunk_text)
    return generate_json(prompt, temperature=0.0)


def generate_scenario(col: chromadb.Collection, scenario_id: int) -> dict | None:
    """Generate one scenario with up to _MAX_RETRIES attempts on validation failure."""
    chunk = _fetch_random_chunk(col)
    text = chunk["text"]
    meta = chunk["metadata"]
    opening = _extract_opening_sentence(text)

    for attempt in range(_MAX_RETRIES):
        raw = _generate_metadata(text)
        if not raw:
            continue
        hint = raw.get("book_hint", "")
        if not validate_hint(hint, text):
            continue
        return {
            "id": scenario_id,
            "source_pdf": meta.get("name", ""),
            "source_page": meta.get("page", 0),
            "book_name": raw.get("book_name", ""),
            "book_hint": hint,
            "association_word": raw.get("association_word", ""),
            "actual_association_word": raw.get("actual_association_word", ""),
            "opening_sentence": raw.get("opening_sentence", opening),
            "full_paragraph": text,
            "warmup_question": raw.get("warmup_question", "What is 7 * 7?"),
        }
    return None


def main() -> None:
    col = _get_collection()
    print(f"Connected to ChromaDB — {col.count()} documents")
    scenarios = []
    for i in range(1, _NUM_SCENARIOS + 1):
        print(f"  Generating scenario {i}/{_NUM_SCENARIOS}...", end=" ", flush=True)
        s = generate_scenario(col, i)
        if s:
            scenarios.append(s)
            print(f"OK  [{s['source_pdf']} p.{s['source_page']}]")
        else:
            print("FAILED (hint validation)")

    os.makedirs(os.path.dirname(_OUT_PATH), exist_ok=True)
    with open(_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(scenarios)} scenarios → {_OUT_PATH}")


if __name__ == "__main__":
    main()
