# Shipping MCP - MCP сервер для отслеживания отправлений

**Коротко:** MCP-сервер, предоставляющий 3 инструмента для трекинга отправлений и оценки ETA. Реализован на FastMCP.

## Инструменты
- `track_package(tracking_number, carrier)` — возвращает статус и последнее событие.
- `estimate_delivery_time(tracking_number, carrier)` — возвращает ETA (по API или эвристике).
- `list_supported_carriers()` — возвращает список поддерживаемых перевозчиков.

## Быстрый старт (локально)
pip install -r requirements.txt
cp .env.example .env
python server.py
# при необходимости заполните TRACKING_API_URL и TRACKING_API_KEY
