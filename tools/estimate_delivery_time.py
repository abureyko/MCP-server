# tools/estimate_delivery_time.py
import os
from typing import Optional
from datetime import datetime, timedelta

import httpx
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from opentelemetry import trace

from mcp_instance import mcp
from .utils import ToolResult

tracer = trace.get_tracer(__name__)

@mcp.tool(
    name="estimate_delivery_time",
    description="""🕒 Оценивает примерную дату доставки по трек-номеру.
Аргументы:
  tracking_number: трек
  carrier: код перевозчика (опционально)
Логика:
  - если API возвращает ETA — используем его
  - иначе — используем среднее время в днях из DEFAULT_TRANSIT_DAYS (env)"""
)
async def estimate_delivery_time(
    tracking_number: str = Field(..., description="Трек-номер отправления"),
    carrier: Optional[str] = Field(None, description="Код перевозчика (опционально)"),
    ctx: Context = None
) -> ToolResult:
    with tracer.start_as_current_span("estimate_delivery_time") as span:
        span.set_attribute("tracking_number", tracking_number)
        await ctx.info("🚀 Оцениваем дату доставки")
        # Попробуем использовать тот же API, что и в track_package
        api_url = os.getenv("TRACKING_API_URL", "").rstrip("/")
        api_key = os.getenv("TRACKING_API_KEY", "")
        if not api_url or not api_key:
            await ctx.warning("⚠️ No API configured — вернём примерную оценку на основе DEFAULT_TRANSIT_DAYS")
            default_days = int(os.getenv("DEFAULT_TRANSIT_DAYS", "5"))
            eta = (datetime.utcnow() + timedelta(days=default_days)).date().isoformat()
            human = f"Оценочная дата доставки (демо): {eta} (±2 дня)."
            return ToolResult(
                content=[TextContent(type="text", text=human)],
                structured_content={"estimated_delivery": eta, "method": "heuristic", "default_days": default_days},
                meta={"demo": True}
            )

        # Реальный API: можно делать тот же GET, но с запросом подробностей
        template = os.getenv("TRACKING_API_QUERY_TEMPLATE", "{api_url}/track?carrier={carrier}&number={tracking_number}")
        resolved = template.format(api_url=api_url, carrier=(carrier or ""), tracking_number=tracking_number)
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        timeout = float(os.getenv("TIMEOUT", "20.0"))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(resolved, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            # Попытка взять ETA
            eta = data.get("estimated_delivery") or data.get("eta")
            if eta:
                human = f"Ориентировочная дата доставки: {eta}."
                return ToolResult(
                    content=[TextContent(type="text", text=human)],
                    structured_content={"estimated_delivery": eta, "method": "api"},
                    meta={"api_used": api_url}
                )
            # Если ETA нет — используем heuristic по carrier
            default_days_map_raw = os.getenv("DEFAULT_TRANSIT_DAYS_MAP", "{}")
            try:
                default_map = eval(default_days_map_raw) if default_days_map_raw else {}
            except Exception:
                default_map = {}
            default_days = int(default_map.get(carrier, os.getenv("DEFAULT_TRANSIT_DAYS", 5)))
            eta2 = (datetime.utcnow() + timedelta(days=int(default_days))).date().isoformat()
            human = f"Оценочная дата доставки (по средней длительности): {eta2} (±2 дня)."
            return ToolResult(
                content=[TextContent(type="text", text=human)],
                structured_content={"estimated_delivery": eta2, "method": "heuristic", "default_days": default_days},
                meta={"api_used": api_url}
            )
        except Exception as e:
            await ctx.error(f"Не удалось получить ETA: {e}")
            raise