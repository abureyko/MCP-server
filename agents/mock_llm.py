# agents/mock_llm.py
# mock LLM для тестов

import asyncio

async def mock_llm(prompt: str) -> str:
    """
    Mock LLM модель для тестирования.
    Возвращает строку, имитирующую ответ LLM.
    """
    await asyncio.sleep(0.1)  # имитация небольшой задержки
    return f"[Mock LLM response for]: {prompt}"
