"""
Trains a heart-disease-risk classifier on the UCI Cleveland Heart Disease dataset.

Dataset: 303 patient records, 13 clinical features, binary outcome.

Feature meanings (standard UCI Cleveland encoding):
    age       - age in years
    sex       - 1 = male, 0 = female
    cp        - chest pain type (0-3; 0 = typical angina ... 3 = asymptomatic)
    trestbps  - resting blood pressure (mm Hg)
    chol      - serum cholesterol (mg/dl)
    fbs       - fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
    restecg   - resting ECG results (0-2)
    thalach   - maximum heart rate achieved
    exang     - exercise-induced angina (1 = yes, 0 = no)
    oldpeak   - ST depression induced by exercise relative to rest
    slope     - slope of the peak exercise ST segment (0-2)
    ca        - number of major vessels (0-3) colored by fluoroscopy
    thal      - thalassemia (1 = normal, 2 = fixed defect, 3 = reversible defect)

IMPORTANT DATA NOTE: this widely-circulated CSV mirror has an inverted `target`
label - empirically, target=1 correlates with FEWER risk markers (lower `ca`,
lower `exang`, higher `thalach`), the opposite of what the column name implies.
We flip it below so 1 consistently means "higher heart disease risk" - verified
by checking group means (see training notes / conversation) before training.

Model: RandomForestClassifier, same rationale as the diabetes model.

Run:
    python train.py

Outputs:
    ../model/heart_disease_model.joblib
    ../evaluation/metrics.json
"""

import json
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "heart_disease.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "model", "heart_disease_model.joblib")
METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "evaluation", "metrics.json")

FEATURE_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]
TARGET_COLUMN = "target"


def train() -> None:
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    # Flip the label - see module docstring for why.
    df[TARGET_COLUMN] = 1 - df[TARGET_COLUMN]

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training on {len(X_train)} samples, evaluating on {len(X_test)} samples...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=4,
        class_weight="balanced",
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
