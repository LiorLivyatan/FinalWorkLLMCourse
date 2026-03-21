"""Quick test: Agno Agent + Knowledge (RAG) over course material."""
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

from agno.agent import Agent
from agno.models.google import Gemini
from knowledge_base import get_knowledge

agent = Agent(
    model=Gemini(id=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")),
    knowledge=get_knowledge(),
    search_knowledge=True,
    instructions=[
        "You are a course material expert.",
        "Always search the knowledge base before answering.",
        "Answer in English, even if the source material is in Hebrew.",
    ],
)

# Test queries
queries = [
    "What is the Q21 game and how does it work?",
    "Explain the MCP (Model Context Protocol) architecture.",
    "What are the scoring weights in the final project?",
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"Q: {q}")
    print(f"{'='*60}")
    response = agent.run(q)
    print(f"A: {response.content}")
