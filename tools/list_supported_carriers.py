# tools/list_supported_carriers.py
from fastmcp import Context
from mcp.types import TextContent
from pydantic import Field

from mcp_instance import mcp
from .utils import ToolResult

@mcp.tool(
    name="list_supported_carriers",
    description="Возвращает список поддерживаемых перевозчиков (берётся из ENV или дефолтного набора)."
)
async def list_supported_carriers(ctx: Context = None) -> ToolResult:
    await ctx.info("📋 Получаем список поддерживаемых перевозчиков")
    carriers_raw = (await _get_carriers_from_env()) if True else None
    human = "✅ Поддерживаемые службы доставки:\n" + "\n".join([f"- {c}" for c in carriers_raw])
    return ToolResult(
        content=[TextContent(type="text", text=human)],
        structured_content={"carriers": carriers_raw}
    )

async def _get_carriers_from_env():
    import os
    raw = os.getenv("SUPPORTED_CARRIERS", "")
    if raw:
        # ожидаем CSV: cdek,post,russian-post,dhl
        return [c.strip() for c in raw.split(",") if c.strip()]
    return ["cdek", "russian-post", "dhl", "ups", "fedex"]