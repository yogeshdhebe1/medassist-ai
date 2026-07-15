# Appointments Module — Update Package

Connects patients and doctors through a bookable appointment flow, and — the interesting design detail — **confirming an appointment automatically creates the doctor↔patient assignment** used by the RBAC checks in the `doctors` module. This means in the real product flow, a doctor doesn't need a separate manual "assign" step (that endpoint was only a dev/testing shortcut) — booking and confirming an appointment is what naturally grants a doctor access to a patient's records.

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/appointments` | Bearer (role: patient) | Book an appointment with a doctor (must be a future date/time) |
| GET | `/v1/appointments` | Bearer (role: patient or doctor) | List your own appointments (patients see their bookings, doctors see appointments booked with them) |
| PATCH | `/v1/appointments/{appointment_id}/status` | Bearer (role: patient or doctor) | Update status: `pending → confirmed → completed`, or `cancelled` |

## How to apply

1. Copy `backend/` content into your repo's `backend/`, overwriting `app/main.py` and `alembic/env.py`, adding the new `app/modules/appointments/` folder.
2. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "create appointments table"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

1. **As patient**: `POST /v1/appointments`
   ```json
   {
     "doctor_id": "a02e0fce-bfa7-495b-b87a-5894df309bd0",
     "scheduled_at": "2026-08-01T10:00:00Z",
     "reason": "Annual checkup"
   }
   ```
   (use your doctor's `id` from `GET /v1/doctors/me`, and any future date)
2. Try a **past date** → should get a 422 validation error (proves the future-date check works).
3. **As patient**: `GET /v1/appointments` → your new appointment should appear with `"status": "pending"`.
4. **Switch to doctor token** (Authorize with the doctor's token): `GET /v1/appointments` → the same appointment should appear here too.
5. **As doctor**: `PATCH /v1/appointments/{appointment_id}/status` with `{"status": "confirmed"}`.
6. **The interesting part** — now test the RBAC connection: if this doctor was *not* already assigned to this patient (fresh test patient), `GET /v1/doctors/me/patients` should now show them, and `POST /v1/doctors/me/patient-notes` for this patient should succeed — proving the appointment confirmation granted the access automatically.
7. Try a **random appointment_id** (someone else's) with a **different doctor's token** → should get 403/404, proving a doctor can't update an appointment that isn't theirs.

## Design notes

- **Status transitions aren't state-machine-enforced here** (e.g. nothing stops going `completed → pending`) — for a resume-scope project this is an acceptable simplification; a production version would validate legal transitions per the state defined in the SRS.
- **Auto-assignment on confirm** is the key design decision worth mentioning in an interview: it means the RBAC relationship (`DoctorPatientAssignment`) is a side effect of a real clinical workflow event (confirming a booking) rather than an arbitrary admin action — this is closer to how the actual product would work.
- Both patient and doctor can update status (e.g. patient cancels, doctor confirms) — the service layer's `_load_and_authorize` ensures whoever calls it can only act on appointments where they are a participant.
