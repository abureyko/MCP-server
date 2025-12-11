# from agents.mock_llm import mock_llm
import re
from tools.track_package import track_package_core
from tools.a2a_adapter import toolresult_to_a2a
from agents.llm import run_llm
from tools.utils import ToolResult
from mcp.types import TextContent

TRACK_RE = re.compile(r"\b(\d{8,})\b")

class OrchestratorAgent:
    """
    Orchestrator — главный агент, который:
    1. Принимает запрос пользователя на естественном языке.
    2. Определяет, какой инструмент MCP вызвать (например, трекинг).
    3. Возвращает результат в формате A2A.
    """
    async def handle_user_request(self, user_input: str) -> dict:
        """
        Обрабатывает пользовательский запрос.
        Если встречается слово "трек" — вызывает track_package.
        В противном случае возвращает ответ mock LLM.
        """
        # 1) Получаем ответ LLM (mock или OpenAI)
        llm_response = await run_llm(user_input)

        # 2) Пытаемся извлечь трек-номер
        match = TRACK_RE.search(user_input)
        if not match:
            # Если трек не найден — возвращаем только LLM-ответ
            return {"llm": llm_response, "tracking": None}

        tracking_number = match.group(1)

        # 3) Локальный вызов core-тулла (демо или реальный при наличии ключей)
        tool_data = await track_package_core(tracking_number)

        # 4) Обёртка ToolResult и преобразование в A2A
        human = f"Трек {tool_data.get('tracking_number')} ({tool_data.get('carrier')}): {tool_data.get('status')}. ETA: {tool_data.get('eta')}"
        tr = ToolResult(content=[TextContent(type="text", text=human)],
                        structured_content=tool_data,
                        meta=tool_data.get("meta", {})
                        )
        a2a = toolresult_to_a2a(tr)

        return {"llm": llm_response, "tracking": a2a}
