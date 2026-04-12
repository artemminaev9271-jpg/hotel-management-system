from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(50), nullable=False, index=True, unique=True)
    role = Column(String(20), default="CLIENT")

    bookings = relationship("Bookings", back_populates="users")
    reviews = relationship("Reviews", back_populates="users")

class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    description = Column(String(100))
    rating = Column(Float)
    image_path = Column(String)

    rooms = relationship("Rooms", back_populates="hotels")
    bookings = relationship("Bookings", back_populates="hotels")
    reviews = relationship("Reviews", back_populates="hotels")

class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey(Hotels.id))
    room_num = Column(Integer, nullable=False)
    room_type = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    hotels = relationship("Hotels", back_populates="rooms")
    bookings = relationship("Bookings", back_populates="rooms")

class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey(Hotels.id))
    room_id = Column(Integer, ForeignKey(Rooms.id))
    user_id = Column(Integer, ForeignKey(Users.id))
    in_date = Column(Date, nullable=False)
    out_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(Date, nullable=False)

    hotels = relationship("Hotels", back_populates="bookings")
    rooms = relationship("Rooms", back_populates="bookings")
    users = relationship("Users", back_populates="bookings")

class Reviews(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(Users.id))
    hotel_id = Column(Integer, ForeignKey(Hotels.id))
    rating = Column(Float, nullable=False)
    comment = Column(String)
    created_at = Column(Date, nullable=False)

    hotels = relationship("Hotels", back_populates="reviews")
    users = relationship("Users", back_populates="reviews")