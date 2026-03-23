# Area: Player AI - Prompt Builders
# PRD: docs/prd-player-ai.md
"""Re-export hub — preserves the original import interface.

All prompt builders are split across:
  - prompts_questions.py   (question + HyDE prompts)
  - prompts_deliberation.py (deliberation + guess prompts)

Import from here as before:
    from prompts import build_questions_prompt, build_guess_prompt, ...
"""

from prompts_questions import (
    build_questions_prompt,
    build_hyde_prompt,
    build_mp_hyde_prompt,
    build_keyword_extraction_prompt,
)
from prompts_deliberation import (
    format_answer,
    build_deliberation_prompt,
    build_council_prompt,
    build_guess_prompt,
)

# Keep the private alias for any code that imports _format_answer directly.
_format_answer = format_answer

__all__ = [
    "build_questions_prompt",
    "build_hyde_prompt",
    "build_mp_hyde_prompt",
    "build_keyword_extraction_prompt",
    "format_answer",
    "_format_answer",
    "build_deliberation_prompt",
    "build_council_prompt",
    "build_guess_prompt",
]
