from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Booking, Slot
from database import SessionLocal

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{email}/bookings")
def get_user_bookings(email: str, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.email == email).all()
    results = []
    for b in bookings:
        slot = db.query(Slot).filter(Slot.id == b.slot_id).first()
        results.append({
            "booking_id": b.id,
            "slot_time": slot.time,
            "slot_id": slot.id
        })
    return results
