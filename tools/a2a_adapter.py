"""
Преобразует ToolResult MCP → формат A2A
"""

from tools.utils import ToolResult

def toolresult_to_a2a(tool_result: ToolResult) -> dict:
    return {
        "messages": [c.text for c in (tool_result.content or [])],
        "structured": tool_result.structured_content or {},
        "meta": tool_result.meta or {},
        "status": "success"
    }
