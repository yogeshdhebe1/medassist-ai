"""
Inference wrapper for the stroke prediction model. Same architecture as the
diabetes/heart disease inference wrappers.
"""

import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "..", "..", "..", "ai_models", "stroke_prediction", "model", "stroke_model.joblib"
)

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def predict_stroke(
    gender: str,
    age: float,
    hypertension: int,
    heart_disease: int,
    ever_married: str,
    work_type: str,
    residence_type: str,
    avg_glucose_level: float,
    bmi: float,
    smoking_status: str,
) -> dict:
    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]
    category_maps = bundle["category_maps"]

    encoded = {
        "age": age,
        "hypertension": hypertension,
        "heart_disease": heart_disease,
        "avg_glucose_level": avg_glucose_level,
        "bmi": bmi,
        "gender": category_maps["gender"].get(gender, 2),  # default to 'Other' code if unrecognized
        "ever_married": category_maps["ever_married"][ever_married],
        "work_type": category_maps["work_type"][work_type],
        "Residence_type": category_maps["Residence_type"][residence_type],
        "smoking_status": category_maps["smoking_status"][smoking_status],
    }

    input_df = pd.DataFrame([[encoded[col] for col in feature_columns]], columns=feature_columns)

    probability = float(model.predict_proba(input_df)[0][1])

    # Thresholds are lower here than the other disease models given the ~5%
    # base rate of stroke in the training population - a 15% predicted
    # probability is already ~3x the population base rate and clinically
    # worth flagging, unlike diabetes/heart disease where the base rate is
    # much higher and a 15% probability would be unremarkable.
    if probability < 0.15:
        risk_level = "low"
    elif probability < 0.35:
        risk_level = "medium"
    else:
        risk_level = "high"

    contributing_factors = []
    if age >= 65:
        contributing_factors.append("Age is the strongest individual stroke risk factor")
    if hypertension == 1:
        contributing_factors.append("Hypertension present")
    if heart_disease == 1:
        contributing_factors.append("Pre-existing heart disease")
    if avg_glucose_level >= 150:
        contributing_factors.append("Elevated average glucose level")
    if bmi >= 30:
        contributing_factors.append("BMI in the obese range")
    if smoking_status in ("smokes", "formerly smoked"):
        contributing_factors.append("Smoking history")

    if not contributing_factors:
        contributing_factors.append("No individual factors strongly elevated; risk driven by combined profile")

    return {
        "risk_level": risk_level,
        "probability": round(probability, 4),
        "contributing_factors": contributing_factors,
        "model_version": "stroke_rf_v1",
    }
