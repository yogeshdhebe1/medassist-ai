"""
Reference ranges for common lab tests, used by the report analyzer to flag
abnormal values. These are general adult reference ranges commonly cited in
clinical lab reports - actual reference ranges vary by lab, method, age, and
sex, so this is deliberately a simplified, general-purpose set for a
resume-scope project, not a clinically-validated exhaustive reference table.
"""

REFERENCE_RANGES = {
    "hemoglobin": {"low": 13.0, "high": 17.0, "unit": "g/dL", "display_name": "Hemoglobin"},
    "glucose": {"low": 70, "high": 100, "unit": "mg/dL", "display_name": "Glucose (Fasting)"},
    "wbc count": {"low": 4000, "high": 11000, "unit": "cells/uL", "display_name": "WBC Count"},
    "platelet count": {"low": 150000, "high": 450000, "unit": "cells/uL", "display_name": "Platelet Count"},
    "creatinine": {"low": 0.7, "high": 1.3, "unit": "mg/dL", "display_name": "Creatinine"},
    "cholesterol total": {"low": 125, "high": 200, "unit": "mg/dL", "display_name": "Total Cholesterol"},
    "blood urea": {"low": 7, "high": 20, "unit": "mg/dL", "display_name": "Blood Urea"},
    "sodium": {"low": 135, "high": 145, "unit": "mEq/L", "display_name": "Sodium"},
    "potassium": {"low": 3.5, "high": 5.0, "unit": "mEq/L", "display_name": "Potassium"},
    "rbc count": {"low": 4.2, "high": 5.9, "unit": "million/uL", "display_name": "RBC Count"},
    "hba1c": {"low": 4.0, "high": 5.6, "unit": "%", "display_name": "HbA1c"},
    "triglycerides": {"low": 0, "high": 150, "unit": "mg/dL", "display_name": "Triglycerides"},
}
