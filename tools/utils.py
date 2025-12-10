# tools/utils.py
# Вспомогательные функции и классы для MCP-инструментов.
import os
import json
from typing import Any, Dict, List
from dataclasses import dataclass

from mcp.types import TextContent
from mcp.shared.exceptions import McpError, ErrorData

@dataclass
class ToolResult:
    """
    Упрощённая обёртка для возвращаемого результата.
    Согласована с примерами MCP: content (list TextContent),
    structured_content (dict), meta (dict).
    """
    content: List[TextContent]
    structured_content: Dict[str, Any] = None
    meta: Dict[str, Any] = None

def _require_env_vars(names: list[str]) -> dict[str, str]:
    """
    Проверка обязательных переменных окружения.
    """
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        raise McpError(
            ErrorData(
                code=-32602,
                message="Отсутствуют обязательные переменные окружения: " + ", ".join(missing)
            )
        )
    return {n: os.getenv(n, "") for n in names}

def format_api_error(response_text: str, status_code: int) -> str:
    """
    Форматирует ошибку API в человекочитаемый вид.
    """
    try:
        data = json.loads(response_text)
        msg = data.get("message") or data.get("error") or str(data)
        return f"Ошибка API (код {status_code}): {msg}"
    except Exception:
        return f"Ошибка API (статус {status_code}): {response_text}"