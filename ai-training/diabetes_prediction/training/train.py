"""
Trains a diabetes-risk classifier on the Pima Indians Diabetes dataset.

Dataset: 768 patient records, 8 clinical features, binary outcome (diabetic / not diabetic).
Model: RandomForestClassifier (chosen for solid baseline accuracy + built-in feature
importance, which we use for the "contributing factors" explanation in the API response).

Run:
    python train.py

Outputs:
    ../model/diabetes_model.joblib   - the trained, ready-to-serve model
    ../evaluation/metrics.json        - accuracy/precision/recall/F1/AUC on the held-out test set
"""

import json
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "pima_diabetes.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "model", "diabetes_model.joblib")
METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "evaluation", "metrics.json")

FEATURE_COLUMNS = [
    "pregnancies",
    "glucose",
    "blood_pressure",
    "skin_thickness",
    "insulin",
    "bmi",
    "diabetes_pedigree",
    "age",
]
TARGET_COLUMN = "outcome"


def load_dataset() -> pd.DataFrame:
    columns = FEATURE_COLUMNS + [TARGET_COLUMN]
    df = pd.read_csv(DATASET_PATH, names=columns)
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """The Pima dataset encodes missing values as 0 for physiologically impossible
    fields (glucose, blood pressure, skin thickness, insulin, BMI can't really be 0).
    We treat those as missing and impute with the column median."""
    cols_with_invalid_zero = ["glucose", "blood_pressure", "skin_thickness", "insulin", "bmi"]
    df = df.copy()
    for col in cols_with_invalid_zero:
        df[col] = df[col].replace(0, pd.NA)
        df[col] = df[col].fillna(df[col].median())
    return df


def train() -> None:
    print("Loading dataset...")
    df = load_dataset()
    df = preprocess(df)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training on {len(X_train)} samples, evaluating on {len(X_test)} samples...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=5,
        class_weight="balanced",  # dataset is ~65/35 imbalanced; this compensates
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importance": dict(
            sorted(
                zip(FEATURE_COLUMNS, model.feature_importances_.round(4).tolist()),
                key=lambda x: x[1],
                reverse=True,
            )
        ),
    }

    print("\n--- Evaluation Metrics ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump({"model": model, "feature_columns": FEATURE_COLUMNS}, MODEL_OUTPUT_PATH)
    print(f"\nModel saved to: {MODEL_OUTPUT_PATH}")

    os.makedirs(os.path.dirname(METRICS_OUTPUT_PATH), exist_ok=True)
    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {METRICS_OUTPUT_PATH}")


if __name__ == "__main__":
    train()
