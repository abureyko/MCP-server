# tests/test_end_to_end.py

import asyncio
from agents.orchestrator import OrchestratorAgent

async def main():
    agent = OrchestratorAgent()
    user_input = "Пожалуйста, трек номер 1234567890"
    response = await agent.handle_user_request(user_input)
    print("=== Результат агента ===")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())



