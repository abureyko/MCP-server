# server.py
# запуск MCP-сервера

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# from fastmcp import Context
from mcp_instance import mcp

# Импорт инструментов (регистрация происходит при импорте)
# Каждый инструмент импортируется отдельно по стандарту
from tools.track_package import track_package  # noqa: F401
from tools.estimate_delivery_time import estimate_delivery_time  # noqa: F401
from tools.list_supported_carriers import list_supported_carriers  # noqa: F401

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

def main():
    init_tracing()
    print("=" * 60)
    print("ЗАПУСК MCP СЕРВЕРА: shipping-agent")
    print("=" * 60)
    print(f"MCP Server: http://{HOST}:{PORT}/mcp (streamable-http)")
    print("=" * 60)

    # Запускаем mcp с рекомендованным transport
    mcp.run(transport="streamable-http", host=HOST, port=PORT, stateless_http=True)

if __name__ == "__main__":
    main()