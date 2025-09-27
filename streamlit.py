import streamlit as st
import requests
from datetime import date, timedelta

st.set_page_config(page_title="Car Rental", page_icon="🚗", layout="centered")
BASE_URL = "http://127.0.0.1:8000"   # FastAPI server

if "user" not in st.session_state:
    st.session_state.user = None
if "selected_car_id" not in st.session_state:
    st.session_state.selected_car_id = None

def api_post(path: str, payload: dict):
    r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
    if not r.ok:
        try:
            detail = r.json().get("detail")
            st.error(detail or f"HTTP {r.status_code}")
        except Exception:
            st.error(f"HTTP {r.status_code}")
        return None
    return r.json()

def api_get(path: str, params: dict | None = None):
    r = requests.get(f"{BASE_URL}{path}", params=params or {}, timeout=10)
    if not r.ok:
        try:
            detail = r.json().get("detail")
            st.error(detail or f"HTTP {r.status_code}")
        except Exception:
            st.error(f"HTTP {r.status_code}")
        return []
    return r.json()

st.title("Car Rental — Prototype")

st.subheader("Account")

if st.session_state.user:
    st.write(f"Signed in as: **{st.session_state.user['name']}**")
    if st.button("Sign out"):
        st.session_state.user = None
        st.rerun()
else:
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Sign in")
        si_email = st.text_input("Email", key="si_email")
        si_pw = st.text_input("Password", type="password", key="si_pw")
        if st.button("Sign in"):
            out = api_post("/api/login", {"email": si_email.strip(), "password": si_pw})
            if out:
                st.session_state.user = out.get("user")
                st.rerun()
    with col2:
        st.caption("Register")
        r_name = st.text_input("Full name", key="r_name")
        r_email = st.text_input("Email", key="r_email")
        r_lic = st.text_input("Driver's license number", key="r_lic")
        r_pw = st.text_input("Password", type="password", key="r_pw")
        if st.button("Create account"):
            out = api_post("/api/register", {
                "name": r_name.strip(),
                "email": r_email.strip(),
                "license_number": r_lic.strip(),
                "password": r_pw
            })
            if out:
                st.session_state.user = out.get("user")
                st.rerun()

st.divider()

# Browse & Select
st.subheader("Find a car")
col1, col2 = st.columns([4, 2])
with col1:
    q = st.text_input("Search (make, model, year, ID)", key="q")
with col2:
    category = st.selectbox("Category", ["All", "Economy", "Sedan", "SUV"], index=0)

cars = api_get("/api/cars", {"q": q, "category": category})
if cars:
    st.table([{
        "ID": c["id"], "Make": c["make"], "Model": c["model"],
        "Year": c["year"], "Category": c.get("category", ""),
        "Status": c["status"]
    } for c in cars])
    available_ids = [c["id"] for c in cars if c["status"] == "available"]
    chosen = st.selectbox("Select car ID to book", ["None"] + available_ids, index=0)
    st.session_state.selected_car_id = None if chosen == "None" else int(chosen)
else:
    st.caption("No cars found.")

st.divider()

# Book
st.subheader("Book")
u = st.session_state.user
if not u:
    st.caption("Sign in to book.")
else:
    cid = st.session_state.selected_car_id
    if not cid:
        st.caption("Select a car ID above.")
    else:
        today = date.today()
        start = st.date_input("Start date", value=today)
        end = st.date_input("End date", value=today + timedelta(days=2), min_value=start)
        if st.button("Confirm booking"):
            out = api_post("/api/book", {
                "car_id": cid,
                "user_id": u["id"],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            })
            if out:
                st.success("Booked.")
                st.session_state.selected_car_id = None
                st.rerun()

st.divider()

# My Reservations
st.subheader("My reservations")
if not st.session_state.user:
    st.caption("Sign in to view your reservations.")
else:
    rows = api_get("/api/my-reservations", {"user_id": st.session_state.user["id"]})
    if rows:
        st.table([{
            "Car ID": r["car_id"], "Type": r.get("vehicle_type", ""),
            "Start": r["start_date"], "End": r["end_date"], "Status": r["status"]
        } for r in rows])
    else:
        st.caption("None.")