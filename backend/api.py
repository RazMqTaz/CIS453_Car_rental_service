from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session
from .database import get_DB
from .models import User

# Import backends classes
from .user import User
from .reservation import Reservation
from .car import Car
from .admin import Admin  # for future use

app = FastAPI(title="Car Rental API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In memory stores (prototype)


class UserStore:
    def __init__(self, db: Session):
        self.db = db

    def register(self, name: str, email: str, license_number: str, password: str) -> User:
        if self.db.query(User).filter(User.email == email).first():
            raise ValueError("Email already registered")
        user = User(name=name, email=email, license_number=license_number, password=password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email, User.password == password).first()
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()


class FleetStore:
    def __init__(self) -> None:
        self.cars: Dict[int, Car] = {}
        self.category: Dict[int, str] = {}

    def add(self, car: Car, category: str) -> None:
        self.cars[car.id] = car
        self.category[car.id] = category

    def search(self, q: str = "", category: Optional[str] = None) -> List[Car]:
        ql = (q or "").strip().lower()
        out = []
        for cid, c in self.cars.items():
            if category and category != "All" and self.category.get(cid) != category:
                continue
            hay = f"{c.make} {c.model} {c.year} {cid}".lower()
            if ql in hay:
                out.append(c)
        # stable sort
        out.sort(key=lambda c: (c.make, c.model, c.year, c.id))
        return out

    def set_status(self, car_id: int, status: str) -> None:
        if car_id in self.cars:
            self.cars[car_id].updateStatus(status)


class ReservationStore:
    def __init__(self) -> None:
        self.rows: List[Reservation] = []

    def add(self, r: Reservation) -> None:
        self.rows.append(r)

    def for_user(self, user_id: int) -> List[Reservation]:
        return [r for r in self.rows if getattr(r, "user_id", None) == user_id]

    def overlaps(self, car_id: int, start: date, end: date) -> bool:
        for r in self.rows:
            if r.car_id != car_id:
                continue
            try:
                rs = date.fromisoformat(r.start_date)
                re = date.fromisoformat(r.end_date)
            except Exception:
                # if stored strings aren't ISO, skip overlap
                continue
            if not (end < rs or re < start):
                return True
        return False


FLEET = FleetStore()
RES = ReservationStore()


def seed(db: Session):
    cars = [
        {"id": 101, "make": "Toyota", "model": "Corolla", "year": 2021, "status": "available", "location": "Economy"},
        {"id": 102, "make": "Honda", "model": "Civic", "year": 2022, "status": "available", "location": "Economy"},
        # Add more cars here
    ]
    for car_data in cars:
        car = Car(**car_data)
        db.add(car)
    db.commit()


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


def car_to_dict(c: Car) -> Dict[str, object]:
    return {
        "id": c.id,
        "make": c.make,
        "model": c.model,
        "year": c.year,
        "status": c.status,
        "category": FLEET.category.get(c.id, ""),
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
def api_register(payload: RegisterIn, db: Session = Depends(get_DB)):
    user_store = UserStore(db)
    try:
        user = user_store.register(
            payload.name, payload.email, payload.license_number, payload.password
        )
        return {"ok": True, "user": user_to_dict(user)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/login")
def api_login(payload: LoginIn, db: Session = Depends(get_DB)):
    user_store = UserStore(db)
    u = user_store.login(payload.email, payload.password)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"ok": True, "user": user_to_dict(u)}


@app.get("/api/cars")
def api_cars(q: str = Query(default=""), category: str = Query(default="All")):
    cars = FLEET.search(q, category)
    return [car_to_dict(c) for c in cars]


@app.post("/api/book")
def api_book(payload: BookIn):
    # validate user
    u = USERS.get_by_id(payload.user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    # validate car
    c = FLEET.cars.get(payload.car_id)
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
    if RES.overlaps(c.id, s, e):
        raise HTTPException(status_code=409, detail="Overlapping reservation")
    # create reservation
    r = Reservation(
        vehicle_type=FLEET.category.get(c.id, "Unknown"),
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
    RES.add(r)
    FLEET.set_status(c.id, "reserved")
    return {"ok": True}


@app.get("/api/my-reservations")
def api_my_reservations(user_id: int = Query(...)):
    rows = RES.for_user(user_id)
    return [res_to_dict(r) for r in rows]
