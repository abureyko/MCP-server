# """
# MCP-tool: Возвращает текущий статус отправления.
# Поддерживает demo-режим и интеграцию с gdeposylka.ru
# """
#
# import os
# from typing import Optional
# import httpx
# from fastmcp import Context
# from pydantic import Field
# from mcp.types import TextContent
# from opentelemetry import trace
#
# from mcp_instance import mcp
# from .utils import ToolResult, format_api_error
# from .gdeposylka_client import GdeposylkaClient  # Подключаем gdeposylka
#
# tracer = trace.get_tracer(__name__)
#
# @mcp.tool(
#     name="track_package",
#     description="""📦 Возвращает текущий статус отправления по трек-номеру.
# Args:
#   tracking_number: Трек-номер (строка)
#   carrier: Код перевозчика (опционально). Если 'auto' или пусто — используется определение/по умолчанию.
# Returns:
#   ToolResult с человекочитаемым текстом и structured_content (raw API)."""
# )
# async def track_package(
#     tracking_number: str = Field(..., description="Трек-номер отправления"),
#     carrier: Optional[str] = Field(None, description="Код перевозчика (опционально, например 'cdek', 'russian-post')"),
#     ctx: Context = None
# ) -> ToolResult:
#     with tracer.start_as_current_span("track_package") as span:
#         span.set_attribute("tracking_number", tracking_number)
#         if carrier:
#             span.set_attribute("carrier", carrier)
#
#         await ctx.info("🚀 Начинаем отслеживание отправления")
#         await ctx.report_progress(progress=0, total=100)
#
#         # Конфигурация API
#         api_key = os.getenv("TRACKING_API_KEY", "")
#
#         # Режим демо (если нет API-ключа) — возвращаем мок
#         if not api_key:
#             await ctx.warning("⚠️ TRACKING_API_KEY не задан — возвращаем демо-ответ")
#             await ctx.report_progress(progress=50, total=100)
#
#             mock = {
#                 "tracking_number": tracking_number,
#                 "carrier": carrier or "demo-carrier",
#                 "status": "in_transit",
#                 "last_event": {
#                     "status": "Прибыло в сортировочный центр",
#                     "location": "Москва",
#                     "datetime": "2025-12-09T10:23:00+03:00"
#                 },
#                 "estimated_delivery": "2025-12-12"
#             }
#
#             await ctx.report_progress(progress=100, total=100)
#             await ctx.info("✅ Демо-ответ готов")
#             human = f"📦 Трек {tracking_number} ({mock['carrier']}): {mock['status']}. " \
#                     f"Последнее событие: {mock['last_event']['status']} — {mock['last_event']['location']} ({mock['last_event']['datetime']}). " \
#                     f"Ожидаемая доставка: {mock['estimated_delivery']}."
#             return ToolResult(
#                 content=[TextContent(type="text", text=human)],
#                 structured_content=mock,
#                 meta={"demo": True}
#             )
#
#         # Если есть API-ключ — используем gdeposylka
#         try:
#             await ctx.info("📡 Отправляем запрос к Gdeposylka API")
#             client = GdeposylkaClient(api_key=api_key)
#             data = await client.track(tracking_number)
#
#             status = data.get("status") or "unknown"
#             last = data.get("last_event") or {}
#             eta = data.get("eta") or data.get("estimated_delivery")
#
#             human = f"📦 Трек {tracking_number}: {status}. "
#             if last:
#                 human += f"Последнее событие: {last.get('status','')} — {last.get('location','')} ({last.get('datetime','')}). "
#             if eta:
#                 human += f"Ожидаемая доставка: {eta}."
#
#             await ctx.report_progress(progress=100, total=100)
#             await ctx.info("✅ Ответ от Gdeposylka получен")
#
#             return ToolResult(
#                 content=[TextContent(type="text", text=human)],
#                 structured_content=data,
#                 meta={"api_used": "gdeposylka.ru"}
#             )
#
#         except httpx.HTTPStatusError as e:
#             await ctx.error(f"❌ HTTP ошибка при обращении к API: {e.response.status_code}")
#             span.set_attribute("error", "http_status_error")
#             raise
#         except Exception as e:
#             await ctx.error(f"💥 Неожиданная ошибка: {e}")
#             span.set_attribute("error", str(e))
#             raise

import os
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from opentelemetry import trace
from mcp_instance import mcp
from .utils import ToolResult
from .gdeposylka_client import GdeposylkaClient

tracer = trace.get_tracer(__name__)

# ------------------- Core функция -------------------
async def track_package_core(tracking_number: str, carrier: str = None) -> dict:
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
