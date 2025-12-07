import requests

MCP = "http://localhost:8000"

def main():
    text = input("Напишите команду: ").lower()

    if "письмо" in text:
        payload = {
            "to": "client@example.com",
            "subject": "От менеджера",
            "body": "Ваш отчёт готов"
        }
        r = requests.post(f"{MCP}/tool/send_email", json=payload)
        print(r.json())

    elif "цен" in text or "акц" in text:
        payload = {"symbol": "AAPL"}
        r = requests.post(f"{MCP}/tool/get_stock_price", json=payload)
        print(r.json())

    elif "встреч" in text or "календар" in text:
        payload = {"title": "Встреча", "date": "2025-01-10"}
        r = requests.post(f"{MCP}/tool/create_calendar_event", json=payload)
        print(r.json())

    else:
        print("Не понял команду")

if __name__ == "__main__":
    main()