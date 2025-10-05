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

## Admin Login
Email: admin@example.com
Password: admin123

## Features (Week 3)
- Register / Login
- View cars
- Book a car
- View my reservations
