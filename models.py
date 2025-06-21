from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)

class Slot(Base):
    __tablename__ = "slots"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    time = Column(DateTime)
    max_bookings = Column(Integer)
    bookings = relationship("Booking", back_populates="slot")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    slot_id = Column(Integer, ForeignKey("slots.id"))
    slot = relationship("Slot", back_populates="bookings")
