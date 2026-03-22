import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q21G-player-whl"))

import knowledge_base
from q21_improvements.scenarios import ALL_SCENARIOS

knowledge_base.ensure_indexed()

print("FINDING TRUE HEBREW OPENING SENTENCES FROM CHROMA DB")
queries = [
    "מגבלת 150 שורות",
    "עקרונות מנחים",
    "Gmail API שרתי HTTP",
    "הסוכן השופט",
    "Model Context Protocol"
]

for i, q in enumerate(queries):
    res = knowledge_base.search(q, n_results=2)
    print(f"\n--- MATCH {i+1} for '{q}' ---")
    for j, r in enumerate(res):
        print(f"Content {j}:\n{r['content'][:250]}\n")

