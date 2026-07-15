# Diabetes Prediction ML Module — Update Package

This adds your **first real ML-powered feature** to the platform: a trained model that predicts diabetes risk from clinical inputs, served through the backend API.

## What's included

### 1. `ai-training/diabetes_prediction/` — the offline training pipeline
This is the part you'd show in an interview to prove you understand the ML side, not just calling a pre-made API:
- `dataset/pima_diabetes.csv` — the Pima Indians Diabetes dataset (768 patient records, 8 clinical features)
- `training/train.py` — trains a `RandomForestClassifier`, evaluates it, saves the model
- `evaluation/metrics.json` — the actual metrics from training (accuracy, precision, recall, F1, ROC-AUC, feature importance)

**Model performance achieved:**
| Metric | Value |
|---|---|
| Accuracy | 72.1% |
| Precision | 58.5% |
| Recall | 70.4% |
| F1 Score | 63.9% |
| **ROC-AUC** | **82.0%** |

ROC-AUC is the metric that matters most here — 0.82 means the model is quite good at ranking higher-risk patients above lower-risk ones, which is what a screening tool needs to do.

**Top predictive features** (from the model itself): glucose (35%), BMI (18%), age (13%), insulin (10%) — this matches real clinical knowledge about diabetes risk factors, which is a good thing to mention if asked about it.

### 2. `backend/app/modules/ai_apis/` — the backend integration
Follows the exact same clean architecture pattern as `patients` and `doctors`:
- `models.py` — `AIPrediction` table (generic, reused for every future AI module — diabetes, heart disease, stroke, etc. all use `prediction_type` to discriminate, per the Database Design doc)
- `schemas.py` — request validation (clinically plausible ranges for every input) and response shape
- `inference.py` — loads the trained `.joblib` model and runs predictions
- `repository.py`, `services.py`, `router.py` — same layering as every other module

### 3. `backend/ai_models/diabetes_prediction/model/diabetes_model.joblib`
The actual trained model file (975 KB) — this is the artifact `inference.py` loads at request time.

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/ai/disease-prediction/diabetes` | Bearer (role: patient) | Run a diabetes risk prediction |
| GET | `/v1/ai/predictions/history` | Bearer (role: patient) | View your past AI predictions |

## How to apply this update

1. Copy `backend/` folder content into your existing repo's `backend/`, overwriting `app/main.py`, `alembic/env.py`, `requirements/base.txt`, and adding the new `app/modules/ai_apis/` and `ai_models/` folders.
2. (Optional but recommended) Also copy the `ai-training/` folder to your **repo root** (not inside `backend/`) — this is what you'll point to in your resume/portfolio as "the ML training pipeline."
3. Install the new ML dependencies:
   ```powershell
   cd backend
   venv\Scripts\activate
   pip install -r requirements\base.txt
   ```
4. Run the migration:
   ```powershell
   alembic revision --autogenerate -m "add ai_predictions table"
   alembic upgrade head
   ```
5. Restart the server:
   ```powershell
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI (`/docs`)

1. Login as your patient user, Authorize with the token.
2. `POST /v1/ai/disease-prediction/diabetes` → "Try it out":
   ```json
   {
     "pregnancies": 6,
     "glucose": 180,
     "blood_pressure": 95,
     "skin_thickness": 35,
     "insulin": 200,
     "bmi": 38.5,
     "diabetes_pedigree": 1.2,
     "age": 55
   }
   ```
   Expected: `"risk_level": "high"`, probability ~0.82, with contributing factors listed.
3. Try a low-risk profile for contrast:
   ```json
   {
     "pregnancies": 0,
     "glucose": 85,
     "blood_pressure": 65,
     "skin_thickness": 20,
     "insulin": 80,
     "bmi": 21.0,
     "diabetes_pedigree": 0.2,
     "age": 25
   }
   ```
   Expected: `"risk_level": "low"`, probability ~0.04.
4. `GET /v1/ai/predictions/history` → should show both predictions you just made.

## How you can retrain the model yourself (to prove you understand it)

```powershell
cd ai-training\diabetes_prediction\training
pip install scikit-learn pandas joblib
python train.py
```
This regenerates `diabetes_model.joblib` and `metrics.json` from scratch — useful to demonstrate in an interview that you can actually reproduce the training, not just that a file exists.

## Design notes (useful for interview/resume talking points)

- **Why RandomForest and not deep learning**: for small tabular datasets (768 rows, 8 features) like this one, tree-based models like Random Forest reliably outperform neural networks, train in seconds without a GPU, and give free feature-importance explainability — which matters for a healthcare use case where "why did the model say this" is a real requirement, not a nice-to-have.
- **Zero-value imputation**: the raw dataset encodes missing values as `0` for fields where 0 is medically impossible (glucose, blood pressure, BMI, etc.). The training script treats these as missing and imputes the column median — this is a real data-quality issue you had to handle, not just "load CSV and fit model."
- **Class imbalance handling**: the dataset is ~65% non-diabetic / 35% diabetic. `class_weight="balanced"` compensates so the model doesn't just learn to always predict "not diabetic."
- **Explainability**: contributing factors are derived from clinically-meaningful thresholds (glucose ≥140, BMI ≥30, etc.) rather than raw SHAP values, keeping the explanation simple and clinically interpretable for a patient-facing UI, per the AI Pipeline doc's emphasis on explainability.
- **Every prediction is persisted** (`ai_predictions` table) with the exact input, output, and model version — full traceability, matching the audit requirements in the Security Architecture doc.
