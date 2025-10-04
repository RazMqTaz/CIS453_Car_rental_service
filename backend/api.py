from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session

# Import backends classes
from .user import User
from .reservation import Reservation
from .car import Car
from .admin import Admin  # for future use
from .database import get_db, init_db
from .db_services import DatabaseUserStore, DatabaseFleetStore, DatabaseReservationStore
from .models import Car as DBCar

app = FastAPI(title="Car Rental API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database services (replacing in-memory stores)
# These will be created per request using dependency injection


def seed_database(db: Session):
    """Seed the database with initial car data"""
    from .models import Car as DBCar
    
    # Check if cars already exist
    existing_cars = db.query(DBCar).count()
    if existing_cars > 0:
        return  # Already seeded
    
    data = [
        (101, "Toyota", "Corolla", 2021, "available", "Economy"),
        (102, "Honda", "Civic", 2022, "available", "Economy"),
        (201, "Toyota", "Camry", 2021, "available", "Sedan"),
        (202, "Nissan", "Altima", 2023, "reserved", "Sedan"),
        (301, "Honda", "CR-V", 2020, "available", "SUV"),
        (302, "Toyota", "RAV4", 2024, "available", "SUV"),
    ]
    for cid, make, model, year, status, cat in data:
        db_car = DBCar(
            id=cid,
            make=make,
            model=model,
            year=year,
            status=status,
            category=cat
        )
        db.add(db_car)
    db.commit()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    # Seed with initial data
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


# Pydantic I/O models (thin)


class RegisterIn(BaseModel):
    name: str
    email: str
    license_number: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class BookIn(BaseModel):
    car_id: int
    user_id: int
    start_date: str  # "YYYY-MM-DD"
    end_date: str  # "YYYY-MM-DD"


def user_to_dict(u: User) -> Dict[str, object]:
    uid = getattr(u, "id", getattr(u, "user_id", None))
    return {
        "id": uid,
        "name": getattr(u, "name", ""),
        "email": getattr(u, "email", ""),
        "license_number": getattr(u, "license_number", ""),
    }


def car_to_dict(c: Car, category: str = "") -> Dict[str, object]:
    return {
        "id": c.id,
        "make": c.make,
        "model": c.model,
        "year": c.year,
        "status": c.status,
        "category": category,
    }


def res_to_dict(r: Reservation) -> Dict[str, object]:
    return {
        "car_id": r.car_id,
        "vehicle_type": getattr(r, "vehicle_type", ""),
        "start_date": r.start_date,
        "end_date": r.end_date,
        "status": r.status,
    }


# Endpoints


@app.post("/api/register")
def api_register(payload: RegisterIn, db: Session = Depends(get_db)):
    try:
        user_store = DatabaseUserStore(db)
        u = user_store.register(
            payload.name, payload.email, payload.license_number, payload.password
        )
        return {"ok": True, "user": user_to_dict(u)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/login")
def api_login(payload: LoginIn, db: Session = Depends(get_db)):
    user_store = DatabaseUserStore(db)
    u = user_store.login(payload.email, payload.password)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"ok": True, "user": user_to_dict(u)}


@app.get("/api/cars")
def api_cars(q: str = Query(default=""), category: str = Query(default="All"), db: Session = Depends(get_db)):
    fleet_store = DatabaseFleetStore(db)
    cars = fleet_store.search(q, category)
    # Get categories for each car
    result = []
    for c in cars:
        car_category = fleet_store.get_category(c.id) or ""
        result.append(car_to_dict(c, car_category))
    return result


@app.post("/api/book")
def api_book(payload: BookIn, db: Session = Depends(get_db)):
    user_store = DatabaseUserStore(db)
    fleet_store = DatabaseFleetStore(db)
    res_store = DatabaseReservationStore(db)
    
    # validate user
    u = user_store.get_by_id(payload.user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    # validate car
    c = fleet_store.get_car(payload.car_id)
    if not c:
        raise HTTPException(status_code=404, detail="Car not found")
    if c.status != "available":
        raise HTTPException(status_code=400, detail="Car not available")
    # check dates
    try:
        s = date.fromisoformat(payload.start_date)
        e = date.fromisoformat(payload.end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid dates")
    if e < s:
        raise HTTPException(status_code=400, detail="End date must be >= start date")
    # overlap check
    if res_store.overlaps(c.id, s, e):
        raise HTTPException(status_code=409, detail="Overlapping reservation")
    # create reservation
    r = Reservation(
        vehicle_type=fleet_store.get_category(c.id) or "Unknown",
        car_id=c.id,
        user_id=user_to_dict(u)["id"],  # type: ignore[arg-type]
        start_date=s.isoformat(),
        end_date=e.isoformat(),
        status="reserved",
    )
    try:
        u.add_reservation(r)  # may not exist
    except Exception:
        if not hasattr(u, "reservations"):
            setattr(u, "reservations", [])
        u.reservations.append(r)  # type: ignore[attr-defined]
    res_store.add(r)
    fleet_store.set_status(c.id, "reserved")
    return {"ok": True}


@app.get("/api/my-reservations")
def api_my_reservations(user_id: int = Query(...), db: Session = Depends(get_db)):
    res_store = DatabaseReservationStore(db)
    rows = res_store.for_user(user_id)
    return [res_to_dict(r) for r in rows]
