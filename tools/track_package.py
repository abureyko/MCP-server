# tools/track_package.py
import os
from typing import Optional

import httpx
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from opentelemetry import trace

from mcp_instance import mcp
from .utils import ToolResult, format_api_error

tracer = trace.get_tracer(__name__)

@mcp.tool(
    name="track_package",
    description="""📦 Возвращает текущий статус отправления по трек-номеру.
Args:
  tracking_number: Трек-номер (строка)
  carrier: Код перевозчика (опционально). Если 'auto' или пусто — используется определение/по умолчанию.
Returns:
  ToolResult с человекочитаемым текстом и structured_content (raw API)."""
)
async def track_package(
    tracking_number: str = Field(..., description="Трек-номер отправления"),
    carrier: Optional[str] = Field(None, description="Код перевозчика (опционально, например 'cdek', 'russian-post')"),
    ctx: Context = None
) -> ToolResult:
    with tracer.start_as_current_span("track_package") as span:
        span.set_attribute("tracking_number", tracking_number)
        if carrier:
            span.set_attribute("carrier", carrier)

        await ctx.info("🚀 Начинаем отслеживание отправления")
        await ctx.report_progress(progress=0, total=100)

        # Конфигурация API: можно задать TRACKING_API_URL и TRACKING_API_KEY в .env
        api_url = os.getenv("TRACKING_API_URL", "").rstrip("/")
        api_key = os.getenv("TRACKING_API_KEY", "")

        # Режим демо (если нет настроек API) — возвращаем мок
        if not api_url or not api_key:
            await ctx.warning("⚠️ TRACKING_API_URL или TRACKING_API_KEY не задан — возвращаем демо-ответ")
            await ctx.report_progress(progress=50, total=100)

            # Простой mock-ответ
            mock = {
                "tracking_number": tracking_number,
                "carrier": carrier or "demo-carrier",
                "status": "in_transit",
                "last_event": {
                    "status": "Прибыло в сортировочный центр",
                    "location": "Москва",
                    "datetime": "2025-12-09T10:23:00+03:00"
                },
                "estimated_delivery": "2025-12-12"
            }

            await ctx.report_progress(progress=100, total=100)
            await ctx.info("✅ Демо-ответ готов")
            human = f"📦 Трек {tracking_number} ({mock['carrier']}): {mock['status']}. " \
                    f"Последнее событие: {mock['last_event']['status']} — {mock['last_event']['location']} ({mock['last_event']['datetime']}). " \
                    f"Ожидаемая доставка: {mock['estimated_delivery']}."
            return ToolResult(
                content=[TextContent(type="text", text=human)],
                structured_content=mock,
                meta={"demo": True}
            )

        # Если есть реальный API — делаем запрос
        try:
            await ctx.info("📡 Отправляем запрос к трекинг-API")
            await ctx.report_progress(progress=25, total=100)

            # Пример: ожидается, что API принимает GET /track?carrier={carrier}&number={tracking_number}
            # Вы можете поменять шаблон запроса через TRACKING_API_QUERY_TEMPLATE в env, если нужно.
            template = os.getenv("TRACKING_API_QUERY_TEMPLATE", "{api_url}/track?carrier={carrier}&number={tracking_number}")
            resolved = template.format(api_url=api_url, carrier=(carrier or ""), tracking_number=tracking_number)

            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            timeout = float(os.getenv("TIMEOUT", "20.0"))

            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(resolved, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            await ctx.report_progress(progress=75, total=100)
            await ctx.info("✅ Получен ответ от API")

            # Пытаемся извлечь стандартные поля (адаптируйте под ваш API)
            status = data.get("status") or data.get("tracking_status") or "unknown"
            last = data.get("last_event") or data.get("last_update") or {}
            eta = data.get("estimated_delivery") or data.get("eta")

            human = f"📦 Трек {tracking_number} ({carrier or 'auto'}): {status}. "
            if last:
                human += f"Последнее событие: {last.get('status','')} — {last.get('location','')} ({last.get('datetime','')}). "
            if eta:
                human += f"Ожидаемая доставка: {eta}."

            await ctx.report_progress(progress=100, total=100)

            return ToolResult(
                content=[TextContent(type="text", text=human)],
                structured_content=data,
                meta={"api_used": api_url}
            )

        except httpx.HTTPStatusError as e:
            await ctx.error(f"❌ HTTP ошибка при обращении к API: {e.response.status_code}")
            span.set_attribute("error", "http_status_error")
            raise
        except Exception as e:
            await ctx.error(f"💥 Неожиданная ошибка: {e}")
            span.set_attribute("error", str(e))
            raise