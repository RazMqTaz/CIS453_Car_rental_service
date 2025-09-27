from pydantic import BaseModel, ConfigDict
from typing import Optional

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

class CarCreate(CarBase): #looks redundant, but if we decide to to change rules we can do it from here without unintentionally breaking shit
    pass

class CarUpdate(BaseModel):
    # fields are all optional so the client can send partial updates to make it easier for them
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
    model_config: ConfigDict(from_attributes=True) # pydantic v2: enables ORM output