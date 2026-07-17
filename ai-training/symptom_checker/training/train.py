"""
Trains a multi-class symptom-to-disease classifier.

Dataset: 4,920 training records + a separate 42-record held-out test set,
132 binary symptom features ("itching", "skin_rash", ... each 0/1), 41 possible
diseases (perfectly balanced: 120 samples per disease in training).

IMPORTANT SCOPING NOTE (documented honestly for interview purposes): the AI
Pipeline doc describes the "real" Symptom Checker as ClinicalBERT/DistilBERT for
free-text NLP understanding, feeding structured features into XGBoost for
classification. Running a transformer model requires either an internet-connected
GPU inference endpoint or a multi-GB local model download, which isn't practical
for a resume-scope local project. This version keeps the XGBoost classification
core (a real, legitimately trained model) but skips the NLP front-end: the API
takes a structured list of symptom names (from the known 132-symptom vocabulary)
rather than parsing free-text symptom descriptions. Swapping in a real NLP layer
later only touches the API's input handling - the trained classifier underneath
doesn't change. This mirrors the same "rule-based now, upgradeable later" honesty
pattern used for the chat module.

Model: XGBoost multi-class classifier (matches the AI Pipeline doc's stated
choice for the classification layer, independent of the NLP front-end question
above).

Run:
    python train.py

Outputs:
    ../model/symptom_checker_model.joblib
    ../evaluation/metrics.json
"""

import json
import os

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_PATH = os.path.join(BASE_DIR, "..", "dataset", "training.csv")
TEST_PATH = os.path.join(BASE_DIR, "..", "dataset", "testing.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "model", "symptom_checker_model.joblib")
METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "evaluation", "metrics.json")

TARGET_COLUMN = "prognosis"


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Drop the stray trailing "Unnamed: 133" junk column present in the
    # training CSV (an artifact of a trailing comma in the source file).
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df


def train() -> None:
    print("Loading dataset...")
    train_df = load_and_clean(TRAIN_PATH)
    test_df = load_and_clean(TEST_PATH)

    symptom_columns = [c for c in train_df.columns if c != TARGET_COLUMN]

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(train_df[TARGET_COLUMN])
    y_test = label_encoder.transform(test_df[TARGET_COLUMN])

    X_train = train_df[symptom_columns]
    X_test = test_df[symptom_columns]

    print(f"Training on {len(X_train)} samples ({len(symptom_columns)} symptoms, "
          f"{len(label_encoder.classes_)} diseases), evaluating on {len(X_test)} held-out samples...")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "f1_macro": round(f1_score(y_test, y_pred, average="macro"), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "num_diseases": len(label_encoder.classes_),
        "num_symptoms": len(symptom_columns),
        "top_10_symptom_importance": dict(
            sorted(
                zip(symptom_columns, model.feature_importances_.round(4).tolist()),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
        ),
    }

    print("\n--- Evaluation Metrics ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(
        {"model": model, "symptom_columns": symptom_columns, "label_encoder": label_encoder},
        MODEL_OUTPUT_PATH,
    )
    print(f"\nModel saved to: {MODEL_OUTPUT_PATH}")

    os.makedirs(os.path.dirname(METRICS_OUTPUT_PATH), exist_ok=True)
    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {METRICS_OUTPUT_PATH}")


if __name__ == "__main__":
    train()
