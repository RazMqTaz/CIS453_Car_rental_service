# Car Rental Service

A full-stack car rental application with persistent database storage, built with FastAPI backend and Streamlit frontend.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip (Python package manager)

### Step 1: Install Dependencies

**Windows:**
```bash
# Install all required packages
py -m pip install -r requirements.txt

# Additional packages needed
py -m pip install sqlalchemy uvicorn
```

**Mac/Linux:**
```bash
# Install all required packages
pip install -r requirements.txt

# Additional packages needed
pip install sqlalchemy uvicorn
```

### Step 2: Run the Backend Server

**Windows:**
```bash
# Start the FastAPI server with database
py -m uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

**Mac/Linux:**
```bash
# Start the FastAPI server with database
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

The server will automatically:
- Create the SQLite database (`cars.db`)
- Seed the database with initial car data
- Start the API server on http://127.0.0.1:8000

### Step 3: Run the Frontend (Optional)

**Windows:**
```bash
# In a new terminal window
py -m streamlit run frontend/streamlit.py
```

**Mac/Linux:**
```bash
# In a new terminal window
streamlit run frontend/streamlit.py
```

### Step 4: Test the API
Visit http://127.0.0.1:8000/docs to see the interactive API documentation.

## 🔧 Troubleshooting

### Common Issues

**"pip is not recognized" (Windows)**
- Use `py -m pip` instead of `pip`
- Or add Python Scripts to your PATH

**"uvicorn is not recognized" (Windows)**
- Use `py -m uvicorn` instead of `uvicorn`

**"Permission denied" (Mac/Linux)**
- Use `pip3` instead of `pip`
- Or add `--user` flag: `pip install --user package_name`

**Port already in use**
- Change port: `--port 8001`
- Or kill existing process: `lsof -ti:8000 | xargs kill` (Mac/Linux)

**Database issues**
- Delete `cars.db` to reset database
- Check file permissions in project directory

## 🏗️ Architecture

### Backend Structure
```
backend/
├── api.py          # FastAPI routes and endpoints
├── database.py     # Database connection and setup
├── models.py       # SQLAlchemy database models
├── db_services.py  # Database service classes
├── base.py         # SQLAlchemy base class
├── car.py          # Car business logic class
├── user.py         # User business logic class
├── reservation.py  # Reservation business logic class
└── schemas.py      # Pydantic models for API
```

### Database Design
- **SQLite Database**: `cars.db` (automatically created)
- **Tables**: `cars`, `users`, `reservations`
- **Persistence**: All data survives server restarts

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cars` | List all cars (with search/filter) |
| POST | `/api/register` | Register new user |
| POST | `/api/login` | User authentication |
| POST | `/api/book` | Book a car reservation |
| GET | `/api/my-reservations` | Get user's reservations |

## 🎯 Features

- **User Management**: Registration, login, authentication
- **Car Fleet**: Browse and search available cars
- **Reservations**: Book cars with date validation
- **Database Persistence**: All data stored in SQLite
- **RESTful API**: Clean API design with FastAPI
- **Interactive Docs**: Auto-generated API documentation

## 🗄️ Database Schema

### Cars Table
- `id` (Primary Key)
- `make`, `model`, `year`
- `status` (available/reserved/maintenance)
- `category` (Economy/Sedan/SUV)

### Users Table
- `id` (Primary Key)
- `name`, `email`, `license_number`
- `password_hash` (secure password storage)
- `role` (customer/admin)

### Reservations Table
- `id` (Primary Key)
- `car_id`, `user_id`
- `start_date`, `end_date`
- `status` (reserved/active/completed)

## 🚀 Development

### Adding New Features
1. Update database models in `models.py`
2. Create database service methods in `db_services.py`
3. Add API endpoints in `api.py`
4. Test with the interactive docs at `/docs`

### Database Migrations
The database is automatically created and seeded on first run. For schema changes:
1. Update models in `models.py`
2. Delete `cars.db` to reset
3. Restart server for fresh database
