from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

# ---- Models ----

class Email(BaseModel):
    to: str
    subject: str
    body: str

class Stock(BaseModel):
    symbol: str

class Calendar(BaseModel):
    title: str
    date: str

# ---- Routes (MCP tools) ----

@app.post("/tool/send_email")
def send_email(data: Email):
    return {
        "success": True,
        "tool": "send_email",
        "request_id": str(uuid.uuid4()),
        "data": {
            "message": f"Email sent to {data.to}"
        }
    }

@app.post("/tool/get_stock_price")
def get_stock_price(data: Stock):
    return {
        "success": True,
        "tool": "get_stock_price",
        "request_id": str(uuid.uuid4()),
        "data": {
            "symbol": data.symbol,
            "price": 123.45
        }
    }

@app.post("/tool/create_calendar_event")
def create_event(data: Calendar):
    return {
        "success": True,
        "tool": "create_calendar_event",
        "request_id": str(uuid.uuid4()),
        "data": {
            "event_id": "event-" + str(uuid.uuid4())
        }
    }