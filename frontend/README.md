# Car Rental Prototype

## Run Backend
```bash
pip install fastapi "uvicorn[standard]"
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

## Run Frontend
```bash
pip install streamlit requests
streamlit run streamlit_frontend.py
```

## Features (Week 3)
- Register / Login
- View cars
- Book a car
- View my reservations
