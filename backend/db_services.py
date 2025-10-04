from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import date
import hashlib
import hashlib

from .models import Car as DBCar, User as DBUser, Reservation as DBReservation
from .car import Car
from .user import User
from .reservation import Reservation

class DatabaseUserStore:
    def __init__(self, db: Session):
        self.db = db

    def register(self, name: str, email: str, license_number: str, password: str) -> User:
        # Check if user already exists
        existing_user = self.db.query(DBUser).filter(DBUser.email == email.strip().lower()).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create database user
        db_user = DBUser(
            name=name,
            email=email.strip().lower(),
            license_number=license_number,
            password_hash=password_hash
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Convert to class-based model
        return User(
            user_id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            license_number=db_user.license_number,
            role=db_user.role
        )

    def login(self, email: str, password: str) -> Optional[User]:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        db_user = self.db.query(DBUser).filter(
            DBUser.email == email.strip().lower(),
            DBUser.password_hash == password_hash
        ).first()
        
        if not db_user:
            return None
            
        return User(
            user_id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            license_number=db_user.license_number,
            role=db_user.role
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if not db_user:
            return None
            
        return User(
            user_id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            license_number=db_user.license_number,
            role=db_user.role
        )


class DatabaseFleetStore:
    def __init__(self, db: Session):
        self.db = db

    def add(self, car: Car, category: str) -> None:
        db_car = DBCar(
            id=car.id,
            make=car.make,
            model=car.model,
            year=car.year,
            status=car.status,
            category=category
        )
        self.db.add(db_car)
        self.db.commit()

    def search(self, q: str = "", category: Optional[str] = None) -> List[Car]:
        query = self.db.query(DBCar)
        
        if category and category != "All":
            query = query.filter(DBCar.category == category)
        
        if q.strip():
            search_term = f"%{q.strip().lower()}%"
            query = query.filter(
                (DBCar.make.ilike(search_term)) |
                (DBCar.model.ilike(search_term)) |
                (DBCar.year.cast(str).ilike(search_term))
            )
        
        db_cars = query.order_by(DBCar.make, DBCar.model, DBCar.year, DBCar.id).all()
        
        # Convert to class-based models
        return [
            Car(
                id=db_car.id,
                make=db_car.make,
                model=db_car.model,
                year=db_car.year,
                status=db_car.status
            )
            for db_car in db_cars
        ]

    def set_status(self, car_id: int, status: str) -> None:
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        if db_car:
            db_car.status = status
            self.db.commit()

    def get_car(self, car_id: int) -> Optional[Car]:
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        if not db_car:
            return None
            
        return Car(
            id=db_car.id,
            make=db_car.make,
            model=db_car.model,
            year=db_car.year,
            status=db_car.status
        )

    def get_category(self, car_id: int) -> Optional[str]:
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        return db_car.category if db_car else None


class DatabaseReservationStore:
    def __init__(self, db: Session):
        self.db = db

    def add(self, r: Reservation) -> None:
        db_reservation = DBReservation(
            vehicle_type=r.vehicle_type,
            car_id=r.car_id,
            user_id=r.user_id,
            start_date=r.start_date,
            end_date=r.end_date,
            status=r.status
        )
        self.db.add(db_reservation)
        self.db.commit()

    def for_user(self, user_id: int) -> List[Reservation]:
        db_reservations = self.db.query(DBReservation).filter(
            DBReservation.user_id == user_id
        ).all()
        
        return [
            Reservation(
                vehicle_type=db_res.vehicle_type,
                car_id=db_res.car_id,
                user_id=db_res.user_id,
                start_date=db_res.start_date,
                end_date=db_res.end_date,
                status=db_res.status
            )
            for db_res in db_reservations
        ]

    def overlaps(self, car_id: int, start: date, end: date) -> bool:
        db_reservations = self.db.query(DBReservation).filter(
            DBReservation.car_id == car_id
        ).all()
        
        for db_res in db_reservations:
            try:
                rs = date.fromisoformat(db_res.start_date)
                re = date.fromisoformat(db_res.end_date)
            except Exception:
                continue
            if not (end < rs or re < start):
                return True
        return False
