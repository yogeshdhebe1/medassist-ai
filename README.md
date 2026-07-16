# Medical Reports Module — Update Package

Adds file upload for medical reports (PDF/JPG/PNG), storage on local disk (a stand-in for S3 in this resume-scope project — the code structure matches what an S3 swap would look like), and RBAC-gated access (only the owning patient or their assigned doctor can view/download a report).

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/reports/upload` | Bearer (role: patient) | Upload a report file (multipart/form-data) |
| GET | `/v1/reports` | Bearer (role: patient) | List your own uploaded reports |
| GET | `/v1/reports/patient/{patient_id}` | Bearer (role: doctor) | List a specific assigned patient's reports |
| GET | `/v1/reports/{report_id}` | Bearer (patient owner or assigned doctor) | Get report metadata |
| GET | `/v1/reports/{report_id}/download` | Bearer (patient owner or assigned doctor) | Download the actual file |

## Validation rules (per the API Design doc)

- Allowed types: PDF, JPG, PNG only
- Max size: 15 MB
- Empty files rejected
- Files stored under a randomized UUID filename (not the original filename) to avoid path traversal / filename collision issues — the original filename is preserved separately in the database for display/download purposes

## How to apply

1. Copy `backend/` content into your repo's `backend/`, overwriting `app/main.py` and `alembic/env.py`, adding `app/modules/medical_reports/` and the `uploads/medical_reports/` folder.
2. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "create medical_reports table"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

File upload endpoints render differently in Swagger — you'll see a **file picker** instead of a JSON body box.

1. **As patient**: `POST /v1/reports/upload` → "Try it out" → click **"Choose File"** and pick any small PDF or image from your computer → optionally set `report_type` (e.g. `blood_test`) → Execute.
   - Try uploading a `.txt` file → should get a 400 `INVALID_FILE` error (proves the MIME type check works).
2. `GET /v1/reports` → your uploaded report should appear.
3. `GET /v1/reports/{report_id}/download` → this one doesn't render nicely in Swagger (it returns a raw file), but you can copy the **cURL command** Swagger generates and run it in a terminal to actually download the file, or open the URL directly in a new browser tab while your Authorize token is active.
4. **RBAC test**: switch to the doctor token and try `GET /v1/reports/patient/{patient_id}` with a patient they're **not** assigned to → should get 403.

## Design notes

- **Local disk storage now, S3-ready structure**: `services.py`'s `upload_report()` is the only place that touches the filesystem. In a real deployment, this function is exactly what you'd swap to call `boto3.client("s3").upload_fileobj(...)` instead of `open(...).write(...)` — the rest of the module (router, repository, RBAC) wouldn't change at all. This separation is worth mentioning if asked "how would you deploy file storage in production."
- **RBAC reuses the doctor↔patient assignment** from the `doctors`/`appointments` modules — a doctor can only see a patient's reports if `DoctorPatientAssignment` exists, same mechanism as patient notes.
- **OCR/AI analysis is intentionally not wired in yet** — per the AI Pipeline doc, `medical_report_ocr` and `medical_report_analyzer` are separate future modules that would consume this table's `file_path` as their input. This module's job is just reliable, secure file storage and retrieval.
