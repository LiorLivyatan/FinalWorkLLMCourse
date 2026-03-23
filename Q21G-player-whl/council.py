# Area: Player AI - Two-Model Council
# PRD: docs/superpowers/specs/2026-03-23-deliberation-improvements-design.md
"""Two-model council: GPT + Gemini deliberate and vote on the best candidate.

resolve_council() merges two votes; council_deliberate() orchestrates the full
council run.  build_council_prompt is imported from prompts (added in Task 5).
"""
import os

import openai_client
import gemini_client

try:
    from prompts import build_council_prompt  # added in Task 5
except ImportError:
    build_council_prompt = None  # type: ignore[assignment]

_DEFAULT_COUNCIL_MODEL = "gemini-3.1-pro-preview"
_DEFAULT_GPT_MODEL = "gpt-4o"


# ---------------------------------------------------------------------------
# Vote resolution
# ---------------------------------------------------------------------------

def resolve_council(gpt_vote: dict, gemini_vote: dict) -> int:
    """Merge two model votes into a single best-candidate index.

    Rules (in priority order):
      1. Agreement      → return the agreed index.
      2. Disagreement   → higher confidence wins.
      3. Tied confidence → GPT wins (return gpt_vote index).

    Args:
        gpt_vote:    Dict with 'best_candidate_index' and 'confidence'.
        gemini_vote: Dict with 'best_candidate_index' and 'confidence'.

    Returns:
        Winning candidate index (int).
    """
    gpt_idx = gpt_vote["best_candidate_index"]
    gem_idx = gemini_vote["best_candidate_index"]

    if gpt_idx == gem_idx:
        return gpt_idx

    gpt_conf = gpt_vote.get("confidence", 0)
    gem_conf = gemini_vote.get("confidence", 0)

    if gem_conf > gpt_conf:
        return gem_idx
    return gpt_idx  # GPT wins on tie or higher confidence


# ---------------------------------------------------------------------------
# Council deliberation
# ---------------------------------------------------------------------------

def council_deliberate(candidates: list, enriched_answers: list) -> dict:
    """Run a two-model council to select the best candidate paragraph.

    Calls GPT-4o and Gemini Pro in parallel (sequentially in this impl),
    resolves their votes, and returns a unified result dict.

    Args:
        candidates:       List of RAG candidate dicts with a 'content' key.
        enriched_answers: List of enriched question dicts.

    Returns:
        Dict with keys:
          - best_candidate_index (int)
          - best_paragraph_text  (str)
          - gpt_vote             (dict)
          - gemini_vote          (dict)
    """
    prompt = build_council_prompt(candidates, enriched_answers)

    gpt_vote = openai_client.generate_json(prompt)
    gemini_model = os.getenv("GEMINI_COUNCIL_MODEL", _DEFAULT_COUNCIL_MODEL)
    gemini_vote = gemini_client.generate_json(prompt, model=gemini_model)

    best_idx = resolve_council(gpt_vote, gemini_vote)
    best_text = candidates[best_idx]["content"] if candidates else ""

    return {
        "best_candidate_index": best_idx,
        "best_paragraph_text": best_text,
        "gpt_vote": gpt_vote,
        "gemini_vote": gemini_vote,
    }
