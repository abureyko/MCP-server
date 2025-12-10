# """
# MCP-tool: Оценка даты доставки по трек-номеру.
# Использует API gdeposylka.ru или среднее время доставки (DEFAULT_TRANSIT_DAYS)
# """
#
# import os
# from typing import Optional
# from datetime import datetime, timedelta
# from fastmcp import Context
# from pydantic import Field
# from mcp.types import TextContent
# from mcp_instance import mcp
# from .utils import ToolResult
# from .gdeposylka_client import GdeposylkaClient  # Подключаем gdeposylka
#
# @mcp.tool(
#     name="estimate_delivery_time",
#     description="🕒 Оценивает примерную дату доставки по трек-номеру."
# )
# async def estimate_delivery_time(
#     tracking_number: str = Field(..., description="Трек-номер"),
#     carrier: Optional[str] = Field(None, description="Код перевозчика"),
#     ctx: Context = None
# ) -> ToolResult:
#     await ctx.info("🚀 Оцениваем дату доставки")
#
#     api_key = os.getenv("TRACKING_API_KEY", "")
#
#     # Demo-режим
#     if not api_key:
#         default_days = int(os.getenv("DEFAULT_TRANSIT_DAYS", 5))
#         eta = (datetime.utcnow() + timedelta(days=default_days)).date().isoformat()
#         human = f"Оценочная дата доставки (демо): {eta} (±2 дня)."
#         return ToolResult(
#             content=[TextContent(type="text", text=human)],
#             structured_content={"estimated_delivery": eta, "method": "heuristic", "default_days": default_days},
#             meta={"demo": True}
#         )
#
#     # Реальный API
#     try:
#         await ctx.info("📡 Получаем ETA через Gdeposylka API")
#         client = GdeposylkaClient(api_key=api_key)
#         data = await client.track(tracking_number)
#         eta = data.get("eta") or data.get("estimated_delivery")
#         human = f"Оценочная дата доставки: {eta}."
#         return ToolResult(
#             content=[TextContent(type="text", text=human)],
#             structured_content={"estimated_delivery": eta, "method": "api"},
#             meta={"api_used": "gdeposylka.ru"}
#         )
#     except Exception as e:
#         await ctx.error(f"💥 Не удалось получить ETA: {e}")
#         # fallback на demo
#         default_days = int(os.getenv("DEFAULT_TRANSIT_DAYS", 5))
#         eta = (datetime.utcnow() + timedelta(days=default_days)).date().isoformat()
#         human = f"Оценочная дата доставки (демо fallback): {eta} (±2 дня)."
#         return ToolResult(
#             content=[TextContent(type="text", text=human)],
#             structured_content={"estimated_delivery": eta, "method": "heuristic", "default_days": default_days},
#             meta={"demo": True}
#         )

from datetime import datetime, timedelta
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from mcp_instance import mcp
from .utils import ToolResult
from .gdeposylka_client import GdeposylkaClient
import os

@mcp.tool(
    name="estimate_delivery_time",
    description="Оценивает примерную дату доставки по трек-номеру."
)
async def estimate_delivery_time(
    tracking_number: str = Field(...),
    carrier: str = Field(None),
    ctx: Context = None
) -> ToolResult:
    await ctx.info("Оцениваем дату доставки")
    api_key = os.getenv("TRACKING_API_KEY", "")

    if not api_key:
        default_days = int(os.getenv("DEFAULT_TRANSIT_DAYS", 5))
        eta = (datetime.utcnow() + timedelta(days=default_days)).date().isoformat()
        human = f"Оценочная дата доставки (демо): {eta} (±2 дня)."
        return ToolResult(content=[TextContent(type="text", text=human)],
                          structured_content={"estimated_delivery": eta, "method": "heuristic"},
                          meta={"demo": True})

    client = GdeposylkaClient(api_key)
    data = await client.track(tracking_number)
    eta = data.get("eta") or data.get("estimated_delivery")
    human = f"Оценочная дата доставки: {eta}."
    return ToolResult(content=[TextContent(type="text", text=human)],
                      structured_content={"estimated_delivery": eta, "method": "api"},
                      meta={"api_used": "gdeposylka.ru"})
