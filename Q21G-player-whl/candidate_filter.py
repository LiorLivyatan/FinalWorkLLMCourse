# Area: Player AI - Candidate Filter
# PRD: docs/superpowers/specs/2026-03-23-deliberation-improvements-design.md
"""Deterministic pre-filter and LLM elimination round for RAG candidates.

Eliminates candidates that violate structural rules implied by the question's
correct answer option.  Always preserves at least one candidate (safety guard).
"""
import os
import re

from prompts import format_answer
from gemini_client import generate_json as gemini_json

_DEFAULT_FILTER_MODEL = "gemini-3.1-flash-lite-preview"

# ---------------------------------------------------------------------------
# Low-level signal detectors
# ---------------------------------------------------------------------------

def _has_numbers(text: str) -> bool:
    return bool(re.search(r'\d{2,}', text))

def _has_list_markers(text: str) -> bool:
    return bool(re.search(r'^\s*[\d•\-\*]', text, re.MULTILINE))

def _has_code(text: str) -> bool:
    return bool(re.search(r'(def |class |import |for |if |return )', text))

def _has_figure_ref(text: str) -> bool:
    return 'איור' in text or 'figure' in text.lower()

# ---------------------------------------------------------------------------
# Keyword → check mapping
# ---------------------------------------------------------------------------

_KEYWORD_CHECKS = {
    'number': _has_numbers,
    'numeric': _has_numbers,
    'digit': _has_numbers,
    'list': _has_list_markers,
    'bullet': _has_list_markers,
    'code': _has_code,
    'function': _has_code,
    'class': _has_code,
    'figure': _has_figure_ref,
    'diagram': _has_figure_ref,
}

# ---------------------------------------------------------------------------
# Public API — deterministic filter
# ---------------------------------------------------------------------------

MIN_SURVIVORS = 3  # council needs choices — never filter below this


def deterministic_filter(candidates: list, enriched_questions: list) -> list:
    """Remove candidates that violate hard constraints.

    Guarantees at least MIN_SURVIVORS so the council has real choices.
    If fewer pass all checks, keeps the top-scoring candidates by
    number of checks passed.
    """
    checks = _build_checks(enriched_questions)
    if not checks:
        return candidates

    # Score each candidate by checks passed
    scored = [(sum(1 for fn in checks if fn(c["content"])), c)
              for c in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)

    all_pass = [c for n, c in scored if n == len(checks)]
    if len(all_pass) >= MIN_SURVIVORS:
        return all_pass
    # Not enough strict survivors — keep top N by score
    return [c for _, c in scored[:max(MIN_SURVIVORS, len(all_pass))]]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_checks(enriched_questions: list) -> list:
    """Derive check functions from the selected answer options."""
    checks = []
    for q in enriched_questions:
        answer = q.get('answer', '')
        if answer in ('D', 'Not Relevant'):
            continue
        option_text = q.get('options', {}).get(answer, '').lower()
        for keyword, fn in _KEYWORD_CHECKS.items():
            if keyword in option_text:
                checks.append(fn)
                break
    return checks

def _passes_all(text: str, checks: list) -> bool:
    return all(fn(text) for fn in checks)

# ---------------------------------------------------------------------------
# LLM elimination round
# ---------------------------------------------------------------------------

def _build_filter_prompt(candidates: list, enriched: list) -> str:
    """Build a constraint-enforcement prompt for the LLM filter round."""
    qa_lines = "\n".join(format_answer(a) for a in enriched)
    cand_lines = "\n\n".join(
        f"Candidate {i}:\n{c['content']}" for i, c in enumerate(candidates)
    )
    return (
        "You are a strict constraint checker for a 21-questions RAG system.\n\n"
        "Q&A constraints that MUST be satisfied by the correct candidate:\n"
        f"{qa_lines}\n\n"
        "Candidates (may be in Hebrew):\n"
        f"{cand_lines}\n\n"
        "Remove any candidate that clearly violates the constraints above.\n"
        "Reply with ONLY valid JSON:\n"
        '{"surviving_indices": [0, 1, ...]}'
    )


def llm_filter(candidates: list, enriched_answers: list) -> list:
    """Call Gemini Flash to eliminate candidates that violate Q&A constraints.

    Skips when ≤3 candidates. Never returns empty — falls back to full list.
    """
    if len(candidates) <= 3:
        return candidates

    prompt = _build_filter_prompt(candidates, enriched_answers)
    model = os.getenv("GEMINI_FILTER_MODEL", _DEFAULT_FILTER_MODEL)
    result = gemini_json(prompt, model=model)

    indices = result.get("surviving_indices", [])
    if not indices:
        return candidates

    filtered = [candidates[i] for i in indices if 0 <= i < len(candidates)]
    return filtered if filtered else candidates
