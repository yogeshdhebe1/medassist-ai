# Stroke Prediction — Update Package

Adds your **third real ML model**: stroke risk prediction, trained on the widely-used Kaggle Stroke Prediction dataset (5,110 patient records).

## Model performance

| Metric | Value |
|---|---|
| Accuracy | 85.5% |
| Precision | 20.5% |
| Recall | **68.0%** |
| F1 Score | 31.5% |
| **ROC-AUC** | **84.6%** |

## ⚠️ Why precision looks "bad" here — an important, honest talking point

This dataset is **heavily imbalanced**: only ~4.9% of patients actually had a stroke. A model that predicted "no stroke" for everyone would score 95% accuracy while being clinically useless. Given that imbalance:

- **Recall (68%)** is the metric that matters most — it means the model correctly flags 68% of patients who actually go on to have a stroke. Missing a real stroke risk (a false negative) is far more costly than a false alarm, per the AI Pipeline doc's stated design principle ("sensitivity/recall prioritized - false negatives are clinically costlier than false positives").
- **Precision (20.5%)** looks low, but this is expected and acceptable for a *screening* tool at this class imbalance: out of everyone the model flags as "at risk," about 1 in 5 will actually have a stroke — which is still a ~4x improvement over flagging at random (the population base rate is ~4.9%), and is the kind of tradeoff real clinical screening tools (e.g. mammography, cardiac stress tests) also make deliberately.
- **Risk-level thresholds are calibrated differently than the other models** — since the population base rate is only ~5%, a 15-35% predicted probability is already meaningfully elevated (see `inference_stroke.py`'s comment on why the thresholds are lower here than diabetes/heart disease).

**Be ready to explain this tradeoff if asked in an interview** — it shows you understand precision/recall tradeoffs on imbalanced medical data, not just that you called `.fit()`.

Top predictive feature: **age (53% importance)** — by far the dominant factor, which matches real-world stroke epidemiology (age is the single strongest stroke risk factor).

## What's included

- `ai-training/stroke_prediction/` — dataset, `train.py`, `metrics.json`
- `backend/ai_models/stroke_prediction/model/stroke_model.joblib`
- `backend/app/modules/ai_apis/`:
  - `inference_stroke.py` — **new file**
  - `schemas.py` — **overwrite**: now has diabetes + heart disease + stroke schemas
  - `services.py` — **overwrite**: adds `predict_stroke_risk()`
  - `router.py` — **overwrite**: adds `POST /v1/ai/disease-prediction/stroke`

## New endpoint

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/ai/disease-prediction/stroke` | Bearer (role: patient) | Run a stroke risk prediction |

## How to apply

1. Copy `backend/ai_models/stroke_prediction/` into your repo's `backend/ai_models/`.
2. In `backend/app/modules/ai_apis/`: add `inference_stroke.py`, overwrite `schemas.py`, `services.py`, `router.py`.
3. **No migration needed** (reuses the `ai_predictions` table with `prediction_type="stroke"`).
4. Restart: `uvicorn app.main:app --reload`

## How to test in Swagger UI

**High-risk profile** (elderly, hypertension, heart disease, high glucose, smoker — expect `"risk_level": "high"`, probability ~0.72):
```json
{
  "gender": "Male",
  "age": 75,
  "hypertension": 1,
  "heart_disease": 1,
  "ever_married": "Yes",
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 220,
  "bmi": 35,
  "smoking_status": "smokes"
}
```

**Low-risk profile** (young, healthy — expect `"risk_level": "low"`, probability ~0.006):
```json
{
  "gender": "Female",
  "age": 25,
  "hypertension": 0,
  "heart_disease": 0,
  "ever_married": "No",
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 85,
  "bmi": 22,
  "smoking_status": "never smoked"
}
```

Then `GET /v1/ai/predictions/history?prediction_type=stroke` to see both.

## Field reference

| Field | Valid values |
|---|---|
| `gender` | `Male`, `Female`, `Other` |
| `ever_married` | `Yes`, `No` |
| `work_type` | `Private`, `Self-employed`, `Govt_job`, `children`, `Never_worked` |
| `residence_type` | `Urban`, `Rural` |
| `smoking_status` | `never smoked`, `formerly smoked`, `smokes`, `Unknown` |
