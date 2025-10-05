from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import date

# ---- Cars ----
class CarBase(BaseModel):
    make: str
    model: str
    year: int
    color: Optional[str] = None
    license_plate: str
    vin: Optional[str] = None
    mileage: int = 0
    fuel_type: str = "Gasoline"
    status: str = "available"
    location: str = "Main"

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None

class CarOut(CarBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---- Users ----
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    license_number: str
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    license_number: str
    role: str
    model_config = ConfigDict(from_attributes=True)

# ---- Reservations ----
class BookIn(BaseModel):
    car_id: int
    user_id: int
    start_date: date
    end_date: date

class ReservationOut(BaseModel):
    id: int
    car_id: int
    user_id: int
    start_date: date
    end_date: date
    status: str
    model_config = ConfigDict(from_attributes=True)

class ReservationUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
