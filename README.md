# Kidney Disease Prediction — Update Package

Adds your **fourth and final disease-prediction ML model** — this completes the full set from the SRS (Diabetes, Heart Disease, Stroke, Kidney Disease).

## ⚠️ Two honest things worth knowing about this one

### 1. This dataset was the messiest to clean
The raw UCI CKD CSV has real data-quality problems:
- The target column has `'ckd'`, `'ckd\t'` (trailing tab), and `'notckd'` — the same class spelled two ways due to a stray tab character. Naively encoding without stripping whitespace would create a spurious 3rd class.
- Categorical columns (`dm`, `cad`) have whitespace variants like `' yes'`, `'\tno'` for the same reason.
- Three supposedly-numeric columns (`pcv`, `wc`, `rc`) are stored as strings because of stray whitespace in some cells — `.astype(float)` would crash; `pd.to_numeric(errors='coerce')` was needed instead.
- Missingness is substantial and uneven (`rbc` ~38% missing, `wc`/`rc` 25-33% missing).

See `train.py`'s docstring and the `clean_string_column()` / `preprocess()` functions for the full cleaning pipeline.

### 2. The model scores ~100% accuracy / ROC-AUC — and that's a legitimate result, not a bug
A perfect score is normally a red flag (data leakage, overfitting, or an accidental giveaway feature). **I checked for this before trusting it**:
- Confirmed the `id` column is not in the feature set.
- Ran 5-fold stratified cross-validation instead of trusting a single train/test split: scores were `[0.9993, 1.0, 0.9993, 1.0, 1.0]` — consistently near-perfect, not a fluke of one lucky split.

This turns out to be a **known characteristic of this specific UCI CKD dataset** — CKD produces very distinctive lab abnormalities (hemoglobin, serum creatinine, urine specific gravity) that separate cleanly from healthy patients, and this is a commonly-cited "easy" benchmark in published papers using the same dataset. Unlike the heart disease and diabetes datasets (real patient data with natural biological overlap between classes), this dataset appears to have been curated with fairly clean separation for teaching purposes.

**This is a good interview talking point**: showing you know that a perfect score demands scrutiny, not celebration, and that you actually did the verification (cross-validation, feature audit) rather than just shipping a suspiciously good number.

## Model performance

| Metric | Value |
|---|---|
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1 Score | 100% |
| ROC-AUC | 100% (5-fold CV mean: 99.97%) |

Top predictive features: `hemo` (hemoglobin), `pcv` (packed cell volume), `sc` (serum creatinine), `sg` (urine specific gravity) — all clinically core CKD diagnostic markers.

## What's included

- `ai-training/kidney_disease_prediction/` — dataset, `train.py`, `metrics.json`
- `backend/ai_models/kidney_disease_prediction/model/kidney_disease_model.joblib`
- `backend/app/modules/ai_apis/`:
  - `inference_kidney.py` — **new file**
  - `schemas.py` — **overwrite**: now has all 4 disease schemas
  - `services.py` — **overwrite**: adds `predict_kidney_disease_risk()`
  - `router.py` — **overwrite**: adds `POST /v1/ai/disease-prediction/kidney-disease`

## New endpoint

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/ai/disease-prediction/kidney-disease` | Bearer (role: patient) | Run a kidney disease risk prediction |

## How to apply

1. Copy `backend/ai_models/kidney_disease_prediction/` into your repo's `backend/ai_models/`.
2. In `backend/app/modules/ai_apis/`: add `inference_kidney.py`, overwrite `schemas.py`, `services.py`, `router.py`.
3. **No migration needed.**
4. Restart: `uvicorn app.main:app --reload`

## How to test in Swagger UI

**High-risk / classic CKD profile** (expect `"risk_level": "high"`, probability ~1.0):
```json
{
  "age": 60, "bp": 90, "sg": 1.010, "al": 3, "su": 1,
  "rbc": "abnormal", "pc": "abnormal", "pcc": "present", "ba": "notpresent",
  "bgr": 150, "bu": 80, "sc": 3.5, "sod": 135, "pot": 5.0,
  "hemo": 9.5, "pcv": 28, "wc": 9800, "rc": 3.5,
  "htn": "yes", "dm": "yes", "cad": "no", "appet": "poor", "pe": "yes", "ane": "yes"
}
```

**Low-risk / healthy profile** (expect `"risk_level": "low"`, probability ~0.008):
```json
{
  "age": 30, "bp": 70, "sg": 1.025, "al": 0, "su": 0,
  "rbc": "normal", "pc": "normal", "pcc": "notpresent", "ba": "notpresent",
  "bgr": 95, "bu": 25, "sc": 0.8, "sod": 140, "pot": 4.2,
  "hemo": 15.5, "pcv": 45, "wc": 7000, "rc": 5.2,
  "htn": "no", "dm": "no", "cad": "no", "appet": "good", "pe": "no", "ane": "no"
}
```

Then `GET /v1/ai/predictions/history?prediction_type=kidney_disease` to see both.

---

## 🎉 All 4 disease-prediction models from the SRS are now complete

| Model | ROC-AUC | Notable engineering detail |
|---|---|---|
| Diabetes | 0.82 | Zero-as-missing-value imputation |
| Heart Disease | 0.91 | Found + fixed an inverted target label |
| Stroke | 0.85 | Severe class imbalance (4.9% positive rate) |
| Kidney Disease | ~1.00 | Messy whitespace/type cleanup + verified near-perfect score isn't leakage |
