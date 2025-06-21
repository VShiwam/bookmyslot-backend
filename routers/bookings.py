from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Booking, Slot
from database import SessionLocal
from schemas import BookingCreate
from sqlalchemy import and_

router = APIRouter(prefix="/events", tags=["Bookings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{event_id}/bookings")
def book_slot(event_id: int, booking: BookingCreate, slot_id: int, db: Session = Depends(get_db)):
    # Get slot
    slot = db.query(Slot).filter(Slot.id == slot_id, Slot.event_id == event_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found for this event")

    # Check duplicate booking
    existing = db.query(Booking).filter(
        and_(
            Booking.email == booking.email,
            Booking.slot_id == slot_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already booked this slot.")

    # Check if slot is full
    current_bookings = db.query(Booking).filter(Booking.slot_id == slot_id).count()
    if current_bookings >= slot.max_bookings:
        raise HTTPException(status_code=400, detail="Slot is full")

    # Add booking
    new_booking = Booking(name=booking.name, email=booking.email, slot_id=slot.id)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {"message": "Booking confirmed", "booking_id": new_booking.id}
