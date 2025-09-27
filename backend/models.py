from sqlalchemy import Column, Integer, String
from .database import Base

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
    status = Column(String(20), default="available")  # available, rented, maintenance
    location = Column(String(100), default="Main") #lot name, or whatever system we come up with for storing cars