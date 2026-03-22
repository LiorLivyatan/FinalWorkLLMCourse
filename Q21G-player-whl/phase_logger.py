# Area: Q21 Eval Pipeline — Diagnostic Logging
# PRD: q21_improvements/improvement_plan.md
"""Glass-box diagnostic logger for PlayerAI pipeline phases.

Writes JSON logs to q21_improvements/debug_logs/. Silently
degrades if directory is not writable (safe for production).
"""
import os
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "debug_logs")


class PhaseLogger:
    """Records internal state of each pipeline phase to JSON."""

    def __init__(self, run_id: str):
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
        except OSError:
            self._enabled = False
            return
        self._enabled = True
        timestamp = datetime.now().strftime("%H%M%S")
        safe_id = "".join(c for c in run_id if c.isalnum() or c in " _-")
        self.filename = os.path.join(LOG_DIR, f"log_{safe_id}_{timestamp}.json")
        self.state = {"run_id": run_id}

    def log_phase(self, phase_name: str, data):
        """Update the JSON log file after each phase."""
        if not self._enabled:
            return
        self.state[phase_name] = data
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
