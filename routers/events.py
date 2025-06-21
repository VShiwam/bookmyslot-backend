from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Event, Slot
from database import SessionLocal, Base, engine
from schemas import EventCreate, EventOut, SlotCreate
from typing import List
from datetime import datetime

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/events", tags=["Events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(title=event.title, description=event.description)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    for slot in event.slots:
        db.add(Slot(event_id=new_event.id, time=slot.time, max_bookings=slot.max_bookings))
    db.commit()
    return new_event

@router.get("/", response_model=List[EventOut])
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@router.get("/{event_id}")
def get_event_with_slots(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    slots = db.query(Slot).filter(Slot.event_id == event_id).all()
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "slots": [
            {"id": s.id, "time": s.time, "max_bookings": s.max_bookings}
            for s in slots
        ]
    }
