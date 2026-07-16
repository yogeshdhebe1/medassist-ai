"""
Inference wrapper for the heart disease prediction model. Same architecture as
diabetes prediction's inference.py - trained offline, loaded once, served per-request.
"""

import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "..", "..", "..", "ai_models", "heart_disease_prediction", "model", "heart_disease_model.joblib"
)

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def predict_heart_disease(
    age: int,
    sex: int,
    cp: int,
    trestbps: float,
    chol: float,
    fbs: int,
    restecg: int,
    thalach: float,
    exang: int,
    oldpeak: float,
    slope: int,
    ca: int,
    thal: int,
) -> dict:
    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    input_df = pd.DataFrame(
        [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]],
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
    if cp == 3:
        contributing_factors.append("Asymptomatic chest pain pattern (often a high-risk presentation)")
    if thal == 3:
        contributing_factors.append("Reversible thalassemia defect")
    if exang == 1:
        contributing_factors.append("Exercise-induced angina present")
    if oldpeak >= 2.0:
        contributing_factors.append("Significant ST depression on exercise")
    if ca >= 1:
        contributing_factors.append(f"{ca} major vessel(s) showing blockage")
    if chol >= 240:
        contributing_factors.append("Elevated cholesterol")
    if thalach < 120:
        contributing_factors.append("Reduced maximum heart rate achieved")

    if not contributing_factors:
        contributing_factors.append("No individual factors strongly elevated; risk driven by combined profile")

    return {
        "risk_level": risk_level,
        "probability": round(probability, 4),
        "contributing_factors": contributing_factors,
        "model_version": "heart_disease_rf_v1",
    }
