"""
Trains a chronic kidney disease (CKD) risk classifier on the UCI CKD dataset.

Dataset: 400 patient records, 24 clinical features, binary outcome (ckd / notckd).

THIS IS THE MESSIEST DATASET IN THIS PROJECT'S ML PIPELINE - worth knowing the
details for an interview:
  1. The target column (`classification`) has values 'ckd', 'ckd\t' (trailing
     tab), and 'notckd' - i.e. the same class is spelled two different ways
     due to a stray tab character in the source data. Naively label-encoding
     without stripping whitespace would silently create a 3rd, spurious class.
  2. Several categorical columns (`dm`, `cad`) have inconsistent whitespace
     variants of the same value (' yes', '\tno', '\tyes') for the same reason.
  3. Three numeric columns (`pcv`, `wc`, `rc`) are stored as strings/objects
     due to stray whitespace in some cells, even though every value is
     numeric - naive `.astype(float)` would crash; `pd.to_numeric(errors='coerce')`
     is needed.
  4. Missingness is substantial and uneven across columns (`rbc` is ~38%
     missing, `wc`/`rc` are 25-33% missing) - median imputation for numeric
     columns, mode imputation for categorical columns.

Feature meanings (standard UCI CKD encoding):
    age   - age (years)                      bp    - blood pressure (mm/Hg)
    sg    - urine specific gravity            al    - albumin (0-5)
    su    - sugar (0-5)                       rbc   - red blood cells (normal/abnormal)
    pc    - pus cell (normal/abnormal)        pcc   - pus cell clumps (present/notpresent)
    ba    - bacteria (present/notpresent)     bgr   - blood glucose random (mg/dl)
    bu    - blood urea (mg/dl)                sc    - serum creatinine (mg/dl)
    sod   - sodium (mEq/L)                    pot   - potassium (mEq/L)
    hemo  - hemoglobin (g/dl)                 pcv   - packed cell volume
    wc    - white blood cell count (cells/cmm) rc   - red blood cell count (millions/cmm)
    htn   - hypertension (yes/no)             dm    - diabetes mellitus (yes/no)
    cad   - coronary artery disease (yes/no)  appet - appetite (good/poor)
    pe    - pedal edema (yes/no)              ane   - anemia (yes/no)

Model: RandomForestClassifier, same rationale as the other disease models.

Run:
    python train.py

Outputs:
    ../model/kidney_disease_model.joblib
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
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "kidney_disease.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "model", "kidney_disease_model.joblib")
METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "evaluation", "metrics.json")

NUMERIC_FEATURES = [
    "age", "bp", "sg", "al", "su", "bgr", "bu", "sc", "sod", "pot",
    "hemo", "pcv", "wc", "rc",
]
BINARY_FEATURES = ["rbc", "pc", "pcc", "ba", "htn", "dm", "cad", "appet", "pe", "ane"]
FEATURE_COLUMNS = NUMERIC_FEATURES + BINARY_FEATURES
TARGET_COLUMN = "classification"

# Fixed category->integer mappings shared with inference.py.
BINARY_MAPS = {
    "rbc": {"normal": 0, "abnormal": 1},
    "pc": {"normal": 0, "abnormal": 1},
    "pcc": {"notpresent": 0, "present": 1},
    "ba": {"notpresent": 0, "present": 1},
    "htn": {"no": 0, "yes": 1},
    "dm": {"no": 0, "yes": 1},
    "cad": {"no": 0, "yes": 1},
    "appet": {"good": 0, "poor": 1},
    "pe": {"no": 0, "yes": 1},
    "ane": {"no": 0, "yes": 1},
}


def clean_string_column(series: pd.Series) -> pd.Series:
    """Strips whitespace/tabs and lowercases - fixes the ' yes' / '\\tno' / 'ckd\\t' issue."""
    return series.astype(str).str.strip().str.lower().replace({"nan": None})


def preprocess(df: pd.DataFrame, fit_medians: dict | None = None) -> tuple[pd.DataFrame, dict]:
    df = df.copy()

    # Fix the numeric-columns-stored-as-strings issue.
    for col in ["pcv", "wc", "rc"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fix inconsistent whitespace in categorical columns.
    for col in BINARY_FEATURES:
        df[col] = clean_string_column(df[col])
        df[col] = df[col].map(BINARY_MAPS[col])

    # Impute: median for numeric (computed on this dataframe, or reused from
    # training if `fit_medians` is passed in - inference.py reuses the medians
    # computed here so a single missing lab value at prediction time doesn't
    # silently use a different reference distribution).
    medians = fit_medians or {}
    for col in NUMERIC_FEATURES:
        median_val = medians.get(col, df[col].median())
        medians[col] = median_val
        df[col] = df[col].fillna(median_val)

    # Mode-impute categorical (0 is the more common/majority class for every
    # one of these binary clinical flags in this dataset).
    for col in BINARY_FEATURES:
        df[col] = df[col].fillna(0)

    return df, medians


def train() -> None:
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    df[TARGET_COLUMN] = clean_string_column(df[TARGET_COLUMN])
    print("Target classes after cleaning:", df[TARGET_COLUMN].unique())
    y = (df[TARGET_COLUMN] == "ckd").astype(int)

    df, medians = preprocess(df)
    X = df[FEATURE_COLUMNS]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training on {len(X_train)} samples, evaluating on {len(X_test)} samples...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=3,
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
    joblib.dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "binary_maps": BINARY_MAPS,
            "medians": medians,
        },
        MODEL_OUTPUT_PATH,
    )
    print(f"\nModel saved to: {MODEL_OUTPUT_PATH}")

    os.makedirs(os.path.dirname(METRICS_OUTPUT_PATH), exist_ok=True)
    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {METRICS_OUTPUT_PATH}")


if __name__ == "__main__":
    train()
