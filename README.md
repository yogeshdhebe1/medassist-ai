# Health Risk Score — Update Package

Adds the last AI module from the SRS that reuses your existing 4 disease-prediction models rather than training anything new — an **aggregation layer**, per the AI Pipeline doc's design: *"Weighted ensemble aggregation of existing disease-prediction model outputs (not a new model trained from scratch)."*

## What it does

`POST /v1/ai/health-risk-score` looks up the patient's **most recent** prediction from each of the 4 disease models (diabetes, heart disease, stroke, kidney disease), maps them to named components (`metabolic`, `cardiac`, `cerebrovascular`, `renal`), and averages them into a single 0-100 overall score.

## Key design details worth knowing

- **Graceful degradation**: if a patient has only run 2 of the 4 disease predictions (say, diabetes and heart disease), the score is still calculated from those 2 — it doesn't fail, and it doesn't silently treat the missing 2 as "0% risk" (which would incorrectly drag the score down). The response tells you exactly which components were used (`components_available`) and which were missing (`components_missing`), so the UI/patient can see the score is partial.
- **Trend tracking**: every calculation is persisted (`health_risk_scores` table), and each new calculation compares itself to the patient's previous score to report `"improving"`, `"stable"`, `"worsening"`, or `"first_calculation"` — this is why it's a table with a timestamp, not just a stateless calculation.
- **No new ML training**: this endpoint calls no model directly — it reads the `confidence_score` already stored on the patient's most recent `AIPrediction` rows (from when they ran the individual disease predictions) and does a weighted average.
- **Equal weighting, documented as tunable**: the AI Pipeline doc describes future weights as "derived from clinical literature on relative risk severity, tunable per admin configuration." For this resume-scope version, all 4 components are weighted equally rather than inventing unsourced severity weights — being upfront about this in an interview is better than presenting made-up clinical weightings as authoritative.

## What's included

- `app/modules/ai_apis/models_risk_score.py` — **new file**: `HealthRiskScore` table
- `app/modules/ai_apis/schemas_risk_score.py` — **new file**: response schema
- `app/modules/ai_apis/repository_risk_score.py` — **new file**
- `app/modules/ai_apis/service_risk_score.py` — **new file**: the aggregation + trend logic
- `app/modules/ai_apis/router.py` — **overwrite**: adds `POST /v1/ai/health-risk-score`

## New endpoint

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/ai/health-risk-score` | Bearer (role: patient) | Aggregate the patient's latest disease predictions into one score |

## How to apply

1. Copy the 4 new files into `backend/app/modules/ai_apis/`.
2. Overwrite `backend/app/modules/ai_apis/router.py`.
3. **Register the new model with Alembic** — open `backend/alembic/env.py` and add this import alongside the other model imports:
   ```python
   from app.modules.ai_apis.models_risk_score import HealthRiskScore  # noqa: F401
   ```
4. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "add health_risk_scores table"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

You need at least one disease prediction already run for this to work (you should have several from earlier testing).

1. As patient: `POST /v1/ai/health-risk-score` (no request body needed) → should return an overall score, with `components_available` listing whichever of `cardiac`/`metabolic`/`renal`/`cerebrovascular` you've run predictions for, and `trend: "first_calculation"` on the first call.
2. Run it again → `trend` should now say `"stable"` (since your underlying predictions haven't changed).
3. Run a **new** heart disease prediction with a much higher risk profile than before, then call `/v1/ai/health-risk-score` again → `trend` should change to `"worsening"`.
4. **Edge case test**: if you test this against a *brand new* patient (register a new test user, don't run any disease predictions) → `POST /v1/ai/health-risk-score` should return **400 `NO_PREDICTIONS_AVAILABLE`** rather than crashing or returning a nonsensical score.
