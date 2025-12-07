# MCP Demo Project

## Как запустить

### 1. Установить зависимости
pip install -r requirements.txt

### 2. Запустить MCP сервер
cd mcp_demo
uvicorn mcp_server:app --reload

### 3. Запустить агента
python agent.py

## Примеры команд

- "отправь письмо клиенту"
- "узнай цену акции"
- "создай встречу"