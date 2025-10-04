from sqlalchemy import Column, Integer, String, Text, DateTime
from .base import Base
from datetime import datetime

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(20), default="available")  # available, rented, maintenance
    category = Column(String(50), default="Unknown")  # Economy, Sedan, SUV, etc.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    license_number = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)  # Store hashed password
    role = Column(String(20), default="customer")
    created_at = Column(DateTime, default=datetime.utcnow)

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    start_date = Column(String(20), nullable=False)  # ISO format string
    end_date = Column(String(20), nullable=False)    # ISO format string
    status = Column(String(20), default="reserved")
    created_at = Column(DateTime, default=datetime.utcnow)