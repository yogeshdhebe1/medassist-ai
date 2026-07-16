# Analytics Module — Update Package

Admin-only dashboard endpoints that aggregate data across every other module — this is the first module that's purely **read-only aggregation**, no new database table of its own.

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/v1/admin/analytics/overview` | Bearer (role: admin) | Platform-wide counts: patients, doctors, appointments, reports, predictions, prescriptions |
| GET | `/v1/admin/analytics/ai-monitoring` | Bearer (role: admin) | Per-AI-module stats: total predictions, average confidence, high-risk count |

## How to apply

1. Copy `backend/app/modules/analytics/` into your repo, and overwrite `app/main.py`.
2. **No migration needed** — this module only reads existing tables.
3. Restart:
   ```powershell
   uvicorn app.main:app --reload
   ```

## You need an admin test user first

You haven't created one yet in this project. Register a new user, then promote it:

1. `POST /v1/auth/register`:
   ```json
   { "email": "admin@example.com", "phone": "+911234567892", "password": "Passw0rd!" }
   ```
2. Promote + verify:
   ```powershell
   psql -U postgres -d medassist -c "UPDATE users SET role = 'admin', is_verified = true WHERE email = 'admin@example.com';"
   ```
3. Login as admin, Authorize with that token.

## How to test in Swagger UI

1. `GET /v1/admin/analytics/overview` → should show real counts based on all the test data you've created so far (e.g. `total_patients: 1`, `appointments_last_30d: 2`, etc.)
2. `GET /v1/admin/analytics/ai-monitoring` → should show a `diabetes` entry with `total_predictions: 2` (from your earlier high-risk and low-risk test predictions) and `high_risk_count: 1`.
3. **RBAC test**: try either endpoint with a **patient or doctor** token → should get 403 (only admins can see platform-wide analytics, per the Security Architecture doc's principle of least privilege).

## Design notes

- **No new table**: analytics is a read-only view over data owned by other modules — it queries `Patient`, `Doctor`, `Appointment`, `MedicalReport`, `AIPrediction`, and `Prescription` directly via SQLAlchemy `func.count()`, rather than duplicating data into an "analytics" table. This keeps the numbers always accurate/live rather than requiring a sync job.
- **JSON aggregation done in Python, not SQL**: `high_risk_count` reads the `risk_level` key out of each prediction's `output_result` JSON column. This is deliberately done in Python (`repository.py`'s docstring explains why) rather than a Postgres JSONB query operator — keeps the code portable if you ever swap databases, at the cost of pulling more rows into memory. Worth mentioning as a scale tradeoff if asked: "how would this need to change for 1M+ predictions?" — the honest answer is you'd move this to a native JSONB query or a materialized summary table at that scale.
- **This is the "Admin" persona's first real feature** — until now every module served patients/doctors. This is a good module to point to if asked "did you build for all three user roles."
