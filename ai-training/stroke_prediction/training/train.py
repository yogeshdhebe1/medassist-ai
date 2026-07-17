"""
Trains a stroke-risk classifier on the (widely-used) Kaggle Stroke Prediction dataset.

Dataset: 5,110 patient records, 11 features (demographic + clinical), binary outcome
(stroke / no stroke). This dataset is HEAVILY IMBALANCED - only ~4.9% of records
are positive (stroke=1). This is realistic (stroke is a relatively rare event at
the population level) but means accuracy is a misleading metric here - a model
that always predicts "no stroke" would already be ~95% "accurate" while being
completely useless. Recall and ROC-AUC matter far more for this model.

Feature meanings:
    gender             - 'Male', 'Female', 'Other'
    age                - age in years
    hypertension       - 1 = has hypertension, 0 = does not
    heart_disease      - 1 = has heart disease, 0 = does not
    ever_married        - 'Yes' / 'No'
    work_type           - 'Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'
    Residence_type      - 'Urban' / 'Rural'
    avg_glucose_level   - average glucose level in blood
    bmi                 - body mass index (has ~4% missing values, median-imputed)
    smoking_status       - 'formerly smoked', 'never smoked', 'smokes', 'Unknown'

Model: RandomForestClassifier with class_weight="balanced" - critical here given
the ~20:1 class imbalance, otherwise the model trivially collapses to predicting
the majority class for everyone.

Run:
    python train.py

Outputs:
    ../model/stroke_model.joblib
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
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "stroke_data.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "model", "stroke_model.joblib")
METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "evaluation", "metrics.json")

NUMERIC_FEATURES = ["age", "hypertension", "heart_disease", "avg_glucose_level", "bmi"]
CATEGORICAL_FEATURES = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "stroke"

# Fixed category->integer mappings, shared with inference.py so encoding is
# identical between training and serving (this is why they're defined as a
# constant here rather than fit dynamically with e.g. sklearn's LabelEncoder,
# which could assign different codes on a different data sample).
CATEGORY_MAPS = {
    "gender": {"Male": 0, "Female": 1, "Other": 2},
    "ever_married": {"No": 0, "Yes": 1},
    "work_type": {"Private": 0, "Self-employed": 1, "Govt_job": 2, "children": 3, "Never_worked": 4},
    "Residence_type": {"Urban": 0, "Rural": 1},
    "smoking_status": {"never smoked": 0, "formerly smoked": 1, "smokes": 2, "Unknown": 3},
}


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["bmi"] = df["bmi"].fillna(df["bmi"].median())
    for col, mapping in CATEGORY_MAPS.items():
        df[col] = df[col].map(mapping)
    return df


def train() -> None:
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    df = preprocess(df)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training on {len(X_train)} samples, evaluating on {len(X_test)} samples...")
    print(f"Positive class rate in training data: {y_train.mean():.3%}")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "positive_class_rate": round(float(y.mean()), 4),
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
    joblib.dump(
        {"model": model, "feature_columns": FEATURE_COLUMNS, "category_maps": CATEGORY_MAPS},
        MODEL_OUTPUT_PATH,
    )
    print(f"\nModel saved to: {MODEL_OUTPUT_PATH}")

    os.makedirs(os.path.dirname(METRICS_OUTPUT_PATH), exist_ok=True)
    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {METRICS_OUTPUT_PATH}")


if __name__ == "__main__":
    train()
