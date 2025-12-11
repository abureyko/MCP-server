import os
from typing import Optional
import httpx
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from opentelemetry import trace

from mcp_instance import mcp
from .utils import ToolResult, format_api_error
from .gdeposylka_client import GdeposylkaClient

tracer = trace.get_tracer(__name__)

# ------------------- Core функция -------------------
async def track_package_core(tracking_number: str, carrier: Optional[str] = None) -> dict:
    """
    Возвращает demo-данные или обращается к API.
    НЕ является MCP-tool.
    """
    if not os.getenv("TRACKING_API_KEY"):
        return {
            "tracking_number": tracking_number,
            "carrier": carrier or "demo-carrier",
            "status": "in_transit",
            "last_event": {
                "status": "Прибыло в сортировочный центр",
                "location": "Москва",
                "datetime": "2025-12-09T10:23:00+03:00"
            },
            "eta": "2025-12-12"
        }

    client = GdeposylkaClient(os.getenv("TRACKING_API_KEY"))
    return await client.track(tracking_number)

# ------------------- MCP-tool -------------------
@mcp.tool(
    name="track_package",
    description="Возвращает текущий статус отправления по трек-номеру."
)
async def track_package(tracking_number: str = Field(...), carrier: str = Field(None), ctx: Context = None) -> ToolResult:
    data = await track_package_core(tracking_number, carrier)
    human = f"📦 Трек {tracking_number} ({data.get('carrier','')}): {data.get('status','unknown')}. ETA: {data.get('eta','')}"
    return ToolResult(content=[TextContent(type="text", text=human)], structured_content=data)
