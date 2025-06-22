from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS: Allow frontend calls from multiple Vercel URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bookmyslot-frontend-7aru.vercel.app",
        "https://bookmyslot-frontend-jz41-b5enic23b-vshiwams-projects.vercel.app",
        "https://bookmyslot-frontend-7aru-c95f3pzgy-vshiwams-projects.vercel.app",
        "http://localhost:5173"  # for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ In-memory storage (will reset on every restart)
events_db = []
bookings_db: Dict[int, List[Dict]] = {}  # event_id -> list of bookings

# ✅ Pydantic Schemas
class Slot(BaseModel):
    time: str  # ISO 8601 format (UTC)
    max_bookings: int

class Event(BaseModel):
    title: str
    description: str
    slots: List[Slot]

class Booking(BaseModel):
    name: str
    email: str
    slot_time: str

# ✅ Root route
@app.get("/")
def root():
    return {"status": "✅ BookMySlot API is live and working!"}

# ✅ Create a new event
@app.post("/events")
def create_event(event: Event):
    events_db.append(event)
    event_id = len(events_db) - 1
    bookings_db[event_id] = []
    return {"message": "Event created", "id": event_id, "event": event}

# ✅ List all events
@app.get("/events")
def get_events():
    return [{"id": i, **event.dict()} for i, event in enumerate(events_db)]

# ✅ Get event details
@app.get("/events/{event_id}")
def get_event(event_id: int):
    if event_id < 0 or event_id >= len(events_db):
        raise HTTPException(status_code=404, detail="Event not found")
    return events_db[event_id]

# ✅ Book a time slot
@app.post("/events/{event_id}/bookings")
def book_slot(event_id: int, booking: Booking):
    if event_id < 0 or event_id >= len(events_db):
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]
    existing = bookings_db[event_id]

    # Prevent duplicate bookings
    for b in existing:
        if b["email"] == booking.email and b["slot_time"] == booking.slot_time:
            raise HTTPException(status_code=400, detail="Already booked this slot")

    # Check if slot exists and has space
    slot = next((s for s in event.slots if s.time == booking.slot_time), None)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    count = sum(1 for b in existing if b["slot_time"] == booking.slot_time)
    if count >= slot.max_bookings:
        raise HTTPException(status_code=400, detail="Slot is full")

    # Accept booking
    bookings_db[event_id].append(booking.dict())
    return {"message": "Booking successful", "booking": booking}

# ✅ (Optional) View bookings by email
@app.get("/users/{email}/bookings")
def get_bookings_by_email(email: str):
    result = []
    for event_id, bookings in bookings_db.items():
        for booking in bookings:
            if booking["email"] == email:
                result.append({
                    "event_id": event_id,
                    "slot_time": booking["slot_time"],
                    "name": booking["name"]
                })
    return result
