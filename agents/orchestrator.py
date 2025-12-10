from agents.mock_llm import mock_llm
from tools.track_package import track_package_core
from tools.a2a_adapter import toolresult_to_a2a
from tools.utils import ToolResult
from mcp.types import TextContent

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
        llm_response = await mock_llm(user_input)

        a2a_trk = None
        if "трек" in user_input.lower():
            # Локальный demo-вызов core функции
            tool_result_data = await track_package_core("1234567890")
            human = f"📦 Трек {tool_result_data['tracking_number']} ({tool_result_data['carrier']}): {tool_result_data['status']}. ETA: {tool_result_data['eta']}"
            tool_result = ToolResult(content=[TextContent(type="text", text=human)],
                                     structured_content=tool_result_data)
            a2a_trk = toolresult_to_a2a(tool_result)

        return {"llm": llm_response, "tracking": a2a_trk}
