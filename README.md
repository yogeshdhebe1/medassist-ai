# Heart Disease Prediction — Update Package

Adds your **second real ML model**: heart disease risk prediction, trained on the UCI Cleveland Heart Disease dataset.

## ⚠️ Important — a real debugging story worth mentioning in interviews

While building this, the model initially predicted **backwards** — a clearly high-risk clinical profile (blocked arteries, exercise-induced chest pain, low max heart rate) came back as "low risk," and vice versa. Investigation showed the specific CSV mirror used has an **inverted `target` label**: patients labeled `target=1` actually had *fewer* risk markers (lower vessel blockage count, less exercise angina, higher max heart rate) than those labeled `0` — the opposite of what the column name implies. This is a known quirk of one popular circulated copy of this dataset.

**Fix**: the label is flipped (`target = 1 - target`) before training, so `1` consistently means "higher heart disease risk" — verified by checking group means (`df.groupby('target')[[...]].mean()`) before and after the fix, and by testing the trained model against a clearly high-risk and clearly low-risk synthetic profile until the direction was correct.

**This is a legitimately good story for a resume/interview**: it shows you don't just trust a dataset blindly — you validate that a model's predictions make clinical sense before shipping it, and you know how to debug a "the model works but gives backwards answers" bug (a much sneakier class of bug than a crash, since the code runs fine and produces plausible-looking, professionally-formatted results — you have to know the domain to catch it).

## Model performance (after the label fix)

| Metric | Value |
|---|---|
| Accuracy | 82.0% |
| Precision | 84.0% |
| Recall | 75.0% |
| F1 Score | 79.3% |
| **ROC-AUC** | **90.9%** |

Top predictive features: `thal` (thalassemia type), `cp` (chest pain type), `thalach` (max heart rate), `ca` (blocked vessel count) — all clinically well-established heart disease risk indicators.

## What's included

- `ai-training/heart_disease_prediction/` — dataset, `train.py` (with the label-fix documented in the docstring), `metrics.json`
- `backend/ai_models/heart_disease_prediction/model/heart_disease_model.joblib` — the trained model artifact
- `backend/app/modules/ai_apis/`:
  - `inference_heart.py` — **new file**, loads and runs the heart disease model
  - `schemas.py` — **overwrite**: now contains both diabetes AND heart disease request/response schemas
  - `services.py` — **overwrite**: refactored with a shared `_persist_and_format()` helper used by both diabetes and heart disease (reduces duplication now that there are 2+ disease models)
  - `router.py` — **overwrite**: adds `POST /v1/ai/disease-prediction/heart-disease`

## New endpoint

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/ai/disease-prediction/heart-disease` | Bearer (role: patient) | Run a heart disease risk prediction |

## How to apply

1. Copy `backend/ai_models/heart_disease_prediction/` into your repo's `backend/ai_models/`.
2. In `backend/app/modules/ai_apis/`: add the new `inference_heart.py`, **overwrite** `schemas.py`, `services.py`, and `router.py` with the versions in this zip.
3. No new database table needed (reuses the existing generic `ai_predictions` table with `prediction_type="heart_disease"`) — **no migration required**.
4. Restart:
   ```powershell
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

**High-risk profile** (should return `"risk_level": "high"`, probability ~0.94):
```json
{
  "age": 65, "sex": 1, "cp": 0, "trestbps": 160, "chol": 280,
  "fbs": 1, "restecg": 1, "thalach": 110, "exang": 1,
  "oldpeak": 3.5, "slope": 1, "ca": 3, "thal": 3
}
```

**Low-risk profile** (should return `"risk_level": "low"`, probability ~0.09):
```json
{
  "age": 35, "sex": 0, "cp": 2, "trestbps": 110, "chol": 180,
  "fbs": 0, "restecg": 0, "thalach": 180, "exang": 0,
  "oldpeak": 0.2, "slope": 2, "ca": 0, "thal": 1
}
```

Then `GET /v1/ai/predictions/history?prediction_type=heart_disease` — should show both predictions.

## Field reference (for filling out test requests)

| Field | Meaning | Range |
|---|---|---|
| `cp` | Chest pain type | 0=typical angina, 1=atypical angina, 2=non-anginal pain, 3=asymptomatic |
| `fbs` | Fasting blood sugar > 120 mg/dl | 0=no, 1=yes |
| `restecg` | Resting ECG result | 0=normal, 1=ST-T abnormality, 2=LV hypertrophy |
| `exang` | Exercise-induced angina | 0=no, 1=yes |
| `slope` | Slope of peak exercise ST segment | 0=upsloping, 1=flat, 2=downsloping |
| `ca` | Major vessels colored by fluoroscopy | 0-4 |
| `thal` | Thalassemia | 1=normal, 2=fixed defect, 3=reversible defect |
