# Car Rental Prototype

## How to Run

### Backend
1. Install dependencies:
   ```bash
   pip install fastapi "uvicorn[standard]"
   ```
2. From the folder with `api.py`, run:
   ```bash
   uvicorn api:app --reload
   ```
3. The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Frontend
1. Open `page.html` in your browser.
2. It’s set to call the backend at `http://127.0.0.1:8000`.
   - If you host the API elsewhere, change `BASE_URL` at the top of `page.html`.

## Notes
- Data is in-memory only, restarting the API clears everything.
- You can also enable mock mode by setting `MOCK = true` in `page.html` to demo without running the backend.
