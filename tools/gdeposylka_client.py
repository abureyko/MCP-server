"""
Простой клиент Gdeposylka API (demo-ready).
Если в окружении нет TRACKING_API_KEY, клиент возвращает mock-ответ.
Если ключ есть, делает реальный запрос (пример, может потребовать правки по API).
"""

import os
import httpx

GDE_BASE = os.getenv("TRACKING_API_URL", "https://gdeposylka.ru").rstrip("/")

class GdeposylkaClient:
    def __init__(self, api_key: str):
        self.api_key = api_key or os.getenv("TRACKING_API_KEY", "")
        self.base_url = GDE_BASE

    async def track(self, tracking_number: str) -> dict:
        """
        Запрос к Gdeposylka. 
        Если нет ключа — вернёт demo-данные
        """
        if not self.api_key:
            return {
                "tracking_number": tracking_number,
                "status": "in_transit",
                "last_event": {
                    "status": "Прибыло в сортировочный центр",
                    "location": "Москва",
                    "datetime": "2025-12-09T10:23:00+03:00"
                },
                "eta": "2025-12-12",
                "meta": {"demo": True}
            }
        # Здесь можно сделать реальный запрос при наличии ключа
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{GDE_BASE}/track/{tracking_number}"
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
