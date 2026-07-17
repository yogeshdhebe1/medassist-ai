"""
Inference wrapper for the kidney disease prediction model. Same architecture as
the other disease-prediction inference wrappers.
"""

import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "..", "..", "..", "ai_models", "kidney_disease_prediction", "model", "kidney_disease_model.joblib"
)

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def predict_kidney_disease(
    age: float,
    bp: float,
    sg: float,
    al: float,
    su: float,
    rbc: str,
    pc: str,
    pcc: str,
    ba: str,
    bgr: float,
    bu: float,
    sc: float,
    sod: float,
    pot: float,
    hemo: float,
    pcv: float,
    wc: float,
    rc: float,
    htn: str,
    dm: str,
    cad: str,
    appet: str,
    pe: str,
    ane: str,
) -> dict:
    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]
    binary_maps = bundle["binary_maps"]

    raw = {
        "age": age, "bp": bp, "sg": sg, "al": al, "su": su, "bgr": bgr, "bu": bu,
        "sc": sc, "sod": sod, "pot": pot, "hemo": hemo, "pcv": pcv, "wc": wc, "rc": rc,
        "rbc": binary_maps["rbc"][rbc], "pc": binary_maps["pc"][pc],
        "pcc": binary_maps["pcc"][pcc], "ba": binary_maps["ba"][ba],
        "htn": binary_maps["htn"][htn], "dm": binary_maps["dm"][dm],
        "cad": binary_maps["cad"][cad], "appet": binary_maps["appet"][appet],
        "pe": binary_maps["pe"][pe], "ane": binary_maps["ane"][ane],
    }

    input_df = pd.DataFrame([[raw[col] for col in feature_columns]], columns=feature_columns)

    probability = float(model.predict_proba(input_df)[0][1])

    if probability < 0.33:
        risk_level = "low"
    elif probability < 0.66:
        risk_level = "medium"
    else:
        risk_level = "high"

    contributing_factors = []
    if hemo < 11:
        contributing_factors.append("Low hemoglobin (anemia is common in CKD)")
    if sc >= 1.5:
        contributing_factors.append("Elevated serum creatinine")
    if sg <= 1.010:
        contributing_factors.append("Low urine specific gravity")
    if al >= 2:
        contributing_factors.append("Significant albumin in urine")
    if htn == "yes":
        contributing_factors.append("Hypertension present")
    if dm == "yes":
        contributing_factors.append("Diabetes mellitus present")
    if pcv < 35:
        contributing_factors.append("Low packed cell volume")

    if not contributing_factors:
        contributing_factors.append("No individual factors strongly elevated; risk driven by combined profile")

    return {
        "risk_level": risk_level,
        "probability": round(probability, 4),
        "contributing_factors": contributing_factors,
        "model_version": "kidney_disease_rf_v1",
    }
