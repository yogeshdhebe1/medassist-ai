"""
Inference wrapper for the diabetes prediction model, used by the ai_apis module.

The model itself is trained offline (see ai-services/diabetes_prediction/training/train.py
in the AI training repo) and the resulting .joblib file is copied here for the backend
to load and serve. This mirrors the real architecture (train offline, deploy the artifact)
while keeping this resume-scope project to a single deployable backend service rather
than a separate microservice.
"""

import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "..", "ai_models", "diabetes_prediction", "model", "diabetes_model.joblib")

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def predict_diabetes(
    pregnancies: int,
    glucose: float,
    blood_pressure: float,
    skin_thickness: float,
    insulin: float,
    bmi: float,
    diabetes_pedigree: float,
    age: int,
) -> dict:
    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    input_df = pd.DataFrame(
        [[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree, age]],
        columns=feature_columns,
    )

    probability = float(model.predict_proba(input_df)[0][1])

    if probability < 0.33:
        risk_level = "low"
    elif probability < 0.66:
        risk_level = "medium"
    else:
        risk_level = "high"

    contributing_factors = []
    if glucose >= 140:
        contributing_factors.append("Elevated glucose level")
    if bmi >= 30:
        contributing_factors.append("BMI in the obese range")
    if age >= 45:
        contributing_factors.append("Age is a risk factor")
    if blood_pressure >= 90:
        contributing_factors.append("Elevated blood pressure")
    if diabetes_pedigree >= 0.8:
        contributing_factors.append("Strong family history of diabetes")

    if not contributing_factors:
        contributing_factors.append("No individual factors strongly elevated; risk driven by combined profile")

    return {
        "risk_level": risk_level,
        "probability": round(probability, 4),
        "contributing_factors": contributing_factors,
        "model_version": "diabetes_rf_v1",
    }
