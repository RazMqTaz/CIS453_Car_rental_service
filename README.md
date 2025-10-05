# Car Rental Prototype

## Run Backend
```bash
pip install fastapi "uvicorn[standard]"
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

## Run Frontend
```bash
pip install streamlit requests
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
