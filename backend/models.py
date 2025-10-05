from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(20), default="customer")
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(30))
    license_plate = Column(String(20), unique=True, index=True, nullable=False)
    vin = Column(String(20), unique=True, index=True)
    mileage = Column(Integer, default=0)
    fuel_type = Column(String(20), default="Gasoline")
    status = Column(String(20), default="available")
    location = Column(String(100), default="Main")
    reservations = relationship("Reservation", back_populates="car", cascade="all, delete-orphan")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="reserved")
    user = relationship("User", back_populates="reservations")
    car = relationship("Car", back_populates="reservations")
