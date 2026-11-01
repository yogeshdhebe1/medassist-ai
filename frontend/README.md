# MedAssist AI — Web Frontend

React 18 + Vite + Tailwind + framer-motion (scroll animations), connected to the real FastAPI backend (no dummy data).

## Run
1. Start the backend first (`uvicorn app.main:app --reload` in `backend/`), running on http://127.0.0.1:8000
2. In this folder (PowerShell):
   ```
   npm install
   copy .env.example .env
   npm run dev
   ```
3. Open http://localhost:3000

## Login
Use the account you registered via Swagger (e.g. test@example.com / Passw0rd!).
Registered users need `is_verified = true` in the DB (no OTP flow implemented).

## CORS
If the browser shows a network error, allow `http://localhost:3000` in the backend CORS settings.

## Known gaps
- Appointments: doctor dropdown needs the new `GET /v1/doctors` backend endpoint (see backend patch); until then it falls back to a pasted doctor ID.
- Doctor/Admin dashboards not built.
