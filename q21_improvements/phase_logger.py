import os
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "debug_logs")
os.makedirs(LOG_DIR, exist_ok=True)

class PhaseLogger:
    """Glass-box diagnostic logger to record internal thoughts of the PlayerAI."""
    
    def __init__(self, run_id: str):
        timestamp = datetime.now().strftime('%H%M%S')
        safe_id = "".join(c for c in run_id if c.isalnum() or c in " _-")
        self.filename = os.path.join(LOG_DIR, f"log_{safe_id}_{timestamp}.json")
        self.state = {
            "run_id": run_id,
            "phase1_questions": [],
            "phase2_answers": [],
            "phase3_queries": [],
            "phase4_candidates": [],
            "phase5_deliberation": {},
            "final_guess": {}
        }
        
    def log_phase(self, phase_name: str, data: any):
        """Update the JSON log file iteratively after each phase."""
        self.state[phase_name] = data
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
