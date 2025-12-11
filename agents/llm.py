# agents/llm.py

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")

client = AsyncOpenAI(
    api_key=LLM_API_KEY
)

async def mock_llm(prompt: str) -> str:
    """mock-llm - используется, если нет ключа"""
    return f"[Mock LLM response for]: {prompt}"

async def call_llm(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a shipping assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1024
    )
    try:
        return response.choices[0].messages.content
    except AttributeError:
        return str(response)

async def run_llm(prompt: str) -> str:
    """"""
    if not LLM_API_KEY or not client:
        return await mock_llm(prompt)
    return await call_llm(prompt)
