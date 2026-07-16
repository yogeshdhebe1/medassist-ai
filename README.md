# Prescriptions Module — Update Package

Lets an assigned doctor write a prescription (list of medications + notes) for a patient, and lets the patient (or the assigned doctor) view them. Reuses the same RBAC pattern as `patient_notes` in the doctors module.

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/prescriptions` | Bearer (role: doctor) | Create a prescription — fails 403 if not assigned to the patient |
| GET | `/v1/prescriptions/me` | Bearer (role: patient) | View your own prescriptions |
| GET | `/v1/prescriptions/patient/{patient_id}` | Bearer (patient owner or assigned doctor) | View a specific patient's prescriptions |

## How to apply

1. Copy `backend/` content into your repo's `backend/`, overwriting `app/main.py` and `alembic/env.py`, adding `app/modules/prescriptions/`.
2. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "create prescriptions table"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

1. **As doctor** (must already be assigned to the patient — e.g. via the appointments confirm flow): `POST /v1/prescriptions`
   ```json
   {
     "patient_id": "b700d2ee-9340-4c24-b7b6-51efeb4f9c72",
     "medications": [
       { "name": "Metformin", "dosage": "500mg", "frequency": "twice daily", "duration_days": 30 },
       { "name": "Atorvastatin", "dosage": "10mg", "frequency": "once daily", "duration_days": 90 }
     ],
     "notes": "Take Metformin with food. Follow up in 4 weeks."
   }
   ```
   Expect **201**.
2. Try the same request with `"medications": []` → expect **422** (proves the "at least one medication" validation works).
3. **As patient**: `GET /v1/prescriptions/me` → the prescription should appear.
4. **RBAC test**: try `POST /v1/prescriptions` as the doctor for a **random/unassigned** `patient_id` → expect **403/404**.

## Design notes

- **`medications` as JSON, not a separate table**: per the Database Design doc's rationale, a prescription's medication list is a variable-length, self-contained unit that's always read/written together with its parent prescription — a separate `medication_items` table with foreign keys would add join complexity with no real query benefit here. `MedicationItem` is still a proper Pydantic model though, so the API still validates and documents its structure precisely (Swagger shows the full nested schema).
- **Same RBAC dependency as patient_notes**: `create_prescription` reuses `doctor_repo.is_assigned(...)` — the exact same check used for patient notes — so a doctor's prescribing rights are governed by the same single assignment relationship as everything else, not a separate permission system.
