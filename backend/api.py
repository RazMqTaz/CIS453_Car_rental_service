from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from .database import get_db, init_db
from . import models
from . import schemas

app = FastAPI(title="Car Rental Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB and seed data on startup
@app.on_event("startup")
def on_startup():
    init_db()
    db = next(get_db())
    try:
        # Seed admin if not present
        if not db.query(models.User).filter_by(email="admin@example.com").first():
            admin = models.User(
                name="Admin",
                email="admin@example.com",
                license_number="ADMIN001",
                password="admin123",  # NOTE: plain text for demo only
                role="admin",
            )
            db.add(admin)
        # Seed cars if table empty
        if db.query(models.Car).count() == 0:
            seed_cars = [
                dict(make="Toyota", model="Corolla", year=2021, color="White", license_plate="ABC101", vin="VIN101", mileage=12000, fuel_type="Gasoline", status="available", location="Economy"),
                dict(make="Honda", model="Civic", year=2022, color="Blue", license_plate="ABC102", vin="VIN102", mileage=8000, fuel_type="Gasoline", status="available", location="Sedan"),
                dict(make="Tesla", model="Model 3", year=2023, color="Red", license_plate="EV303", vin="VIN303", mileage=5000, fuel_type="Electric", status="available", location="EV"),
                dict(make="Ford", model="Escape", year=2020, color="Gray", license_plate="SUV404", vin="VIN404", mileage=25000, fuel_type="Gasoline", status="available", location="SUV"),
            ]
            for c in seed_cars:
                db.add(models.Car(**c))
        db.commit()
    finally:
        db.close()

# ----- Auth -----
@app.post("/api/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="Email already in use")
    if db.query(models.User).filter_by(license_number=user.license_number).first():
        raise HTTPException(status_code=400, detail="License already in use")
    u = models.User(**user.dict(), role="customer")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@app.post("/api/login", response_model=schemas.UserOut)
def login(creds: schemas.LoginIn, db: Session = Depends(get_db)):
    u = db.query(models.User).filter_by(email=creds.email, password=creds.password).first()
    if not u:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return u

# ----- Cars -----
@app.get("/api/cars", response_model=List[schemas.CarOut])
def list_cars(q: Optional[str] = Query(None), category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    qs = db.query(models.Car)
    if category and category not in ("All", ""):
        qs = qs.filter(models.Car.location == category)
    if q:
        like = f"%{q}%"
        qs = qs.filter(
            (models.Car.make.ilike(like)) |
            (models.Car.model.ilike(like)) |
            (models.Car.license_plate.ilike(like))
        )
    return qs.all()

# ----- Booking -----
@app.post("/api/book", response_model=dict)
def book(req: schemas.BookIn, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter_by(id=req.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.status != "available":
        raise HTTPException(status_code=400, detail="Car not available")

    # Check overlap
    overlap = db.query(models.Reservation).filter(
        models.Reservation.car_id == req.car_id,
        models.Reservation.end_date >= req.start_date,
        models.Reservation.start_date <= req.end_date,
    ).first()
    if overlap:
        raise HTTPException(status_code=400, detail="Dates overlap with an existing reservation")

    r = models.Reservation(
        car_id=req.car_id,
        user_id=req.user_id,
        start_date=req.start_date,
        end_date=req.end_date,
        status="reserved",
    )
    db.add(r)
    car.status = "reserved"
    db.commit()
    return {"ok": True}

@app.get("/api/my-reservations", response_model=List[schemas.ReservationOut])
def my_reservations(user_id: int = Query(...), db: Session = Depends(get_db)):
    rows = db.query(models.Reservation).filter_by(user_id=user_id).all()
    return rows

# ----- Admin -----
@app.get("/api/admin/reservations", response_model=List[schemas.ReservationOut])
def all_reservations(admin_email: str = Query(...), admin_password: str = Query(...), db: Session = Depends(get_db)):
    admin = db.query(models.User).filter_by(email=admin_email, password=admin_password, role="admin").first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin credentials required")
    return db.query(models.Reservation).all()

@app.put("/api/admin/reservations/{res_id}", response_model=schemas.ReservationOut)
def update_reservation(res_id: int, update: schemas.ReservationUpdate, admin_email: str = Query(...), admin_password: str = Query(...), db: Session = Depends(get_db)):
    admin = db.query(models.User).filter_by(email=admin_email, password=admin_password, role="admin").first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin credentials required")
    r = db.query(models.Reservation).filter_by(id=res_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if update.start_date is not None:
        r.start_date = update.start_date
    if update.end_date is not None:
        r.end_date = update.end_date
    if update.status is not None:
        r.status = update.status
    db.commit()
    db.refresh(r)
    return r
