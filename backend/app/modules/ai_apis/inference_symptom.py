"""
Inference wrapper for the symptom checker model. Takes a list of symptom names
(from the known 132-symptom vocabulary the model was trained on) and returns the
top-3 most likely diseases with confidence scores.
"""

import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "..", "..", "..", "ai_models", "symptom_checker", "model", "symptom_checker_model.joblib"
)

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def get_known_symptoms() -> list[str]:
    """Returns the full vocabulary of symptom names the model understands -
    used by the /symptom-checker/symptoms endpoint so a frontend can render
    a checklist instead of guessing valid symptom strings."""
    bundle = _load_model()
    return bundle["symptom_columns"]


def predict_disease(symptoms: list[str]) -> dict:
    bundle = _load_model()
    model = bundle["model"]
    symptom_columns = bundle["symptom_columns"]
    label_encoder = bundle["label_encoder"]

    known_symptoms_set = set(symptom_columns)
    unrecognized = [s for s in symptoms if s not in known_symptoms_set]
    recognized = [s for s in symptoms if s in known_symptoms_set]

    # Build the binary feature vector (1 if the symptom was reported, else 0).
    input_row = {col: (1 if col in recognized else 0) for col in symptom_columns}
    input_df = pd.DataFrame([input_row], columns=symptom_columns)

    probabilities = model.predict_proba(input_df)[0]

    # Top 3 predictions, ranked by probability.
    top_indices = probabilities.argsort()[::-1][:3]
    predictions = []
    for idx in top_indices:
        disease_name = label_encoder.inverse_transform([idx])[0]
        confidence = float(probabilities[idx])
        predictions.append(
            {
                "disease": disease_name,
                "confidence": round(confidence, 4),
                "explanation": (
                    f"Based on {len(recognized)} reported symptom(s), the model estimates a "
                    f"{confidence:.0%} likelihood of {disease_name}."
                ),
            }
        )

    # Advisory flag: recommend seeing a doctor if the top prediction's
    # confidence is high, or if very few recognizable symptoms were given
    # (meaning the prediction itself is less reliable and a professional
    # assessment matters more).
    top_confidence = predictions[0]["confidence"] if predictions else 0.0
    recommend_doctor_visit = top_confidence >= 0.4 or len(recognized) <= 2

    return {
        "predictions": predictions,
        "recommend_doctor_visit": recommend_doctor_visit,
        "recognized_symptoms": recognized,
        "unrecognized_symptoms": unrecognized,
        "model_version": "symptom_checker_xgb_v1",
    }
