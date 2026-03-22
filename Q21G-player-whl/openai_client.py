import os
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

# Initialize the OpenAI client
# It will automatically look for OPENAI_API_KEY in the environment
client = OpenAI()

def generate(prompt: str, model: str = "gpt-5.4-2026-03-05") -> str:
    """Standard text generation call."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_json(prompt: str, model: str = "gpt-5.4-2026-03-05") -> dict:
    """JSON-enforced generation call."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Failed to decode JSON from OpenAI response.")
        return {}
