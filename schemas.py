from pydantic import BaseModel
from typing import List
from datetime import datetime

class SlotCreate(BaseModel):
    time: datetime
    max_bookings: int

class EventCreate(BaseModel):
    title: str
    description: str
    slots: List[SlotCreate]

class BookingCreate(BaseModel):
    name: str
    email: str

class EventOut(BaseModel):
    id: int
    title: str
    description: str

    model_config = {
        "from_attributes": True  # ✅ Pydantic v2
    }
