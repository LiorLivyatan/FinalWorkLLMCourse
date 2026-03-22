# Area: Player AI - Candidate Filter
# PRD: docs/superpowers/specs/2026-03-23-deliberation-improvements-design.md
"""Deterministic pre-filter for RAG candidates based on hard Q&A constraints.

Eliminates candidates that violate structural rules implied by the question's
correct answer option.  Always preserves at least one candidate (safety guard).
"""
import re

# ---------------------------------------------------------------------------
# Low-level signal detectors
# ---------------------------------------------------------------------------

def _has_numbers(text: str) -> bool:
    """True when text contains a sequence of 2+ digits."""
    return bool(re.search(r'\d{2,}', text))


def _has_list_markers(text: str) -> bool:
    """True when text contains bullet / numbered-list markers."""
    return bool(re.search(r'^\s*[\d•\-\*]', text, re.MULTILINE))


def _has_code(text: str) -> bool:
    """True when text contains Python / code keywords."""
    return bool(re.search(r'(def |class |import |for |if |return )', text))


def _has_figure_ref(text: str) -> bool:
    """True when text references a figure (Hebrew or English)."""
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
# Public API
# ---------------------------------------------------------------------------

def deterministic_filter(candidates: list, enriched_questions: list) -> list:
    """Remove candidates that violate hard constraints derived from enriched_questions.

    Args:
        candidates: List of RAG candidate dicts, each with a 'content' key.
        enriched_questions: List of question dicts with keys:
            - answer (str): selected answer letter, e.g. "B"
            - options (dict): mapping of letter -> option text
            - question_text (str)

    Returns:
        Filtered list of candidates.  Never empty — falls back to the full
        input list if all candidates would be removed.
    """
    checks = _build_checks(enriched_questions)
    if not checks:
        return candidates

    filtered = [c for c in candidates if _passes_all(c['content'], checks)]

    # Safety guard: never return an empty list
    return filtered if filtered else candidates


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_checks(enriched_questions: list) -> list:
    """Derive a list of check functions from the selected answer options.

    Skips questions whose answer is "D" or "Not Relevant".
    """
    checks = []
    for q in enriched_questions:
        answer = q.get('answer', '')
        if answer in ('D', 'Not Relevant'):
            continue
        options = q.get('options', {})
        option_text = options.get(answer, '').lower()
        for keyword, fn in _KEYWORD_CHECKS.items():
            if keyword in option_text:
                checks.append(fn)
                break  # one check per question is enough
    return checks


def _passes_all(text: str, checks: list) -> bool:
    """Return True only when text satisfies every check."""
    return all(fn(text) for fn in checks)
