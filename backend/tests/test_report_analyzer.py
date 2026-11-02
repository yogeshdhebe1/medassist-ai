import os
import shutil

import pytest

from app.modules.medical_reports.analyzer import analyze_extracted_values
from app.modules.medical_reports.reference_ranges import REFERENCE_RANGES


def _field(key, value):
    r = REFERENCE_RANGES[key]
    return {"value": value, "unit": r["unit"], "display_name": r["display_name"]}


def test_flags_high_low_and_normal():
    out = analyze_extracted_values({
        "hemoglobin": _field("hemoglobin", 9.0),      # low
        "glucose": _field("glucose", 180),             # high
        "creatinine": _field("creatinine", 1.0),       # normal
    })
    flags = {v["test"]: v["flag"] for v in out["abnormal_values"]}
    assert flags == {"Hemoglobin": "low", "Glucose (Fasting)": "high"}
    assert [v["test"] for v in out["normal_values"]] == ["Creatinine"]
    assert out["summary"]


def test_boundary_values_are_normal():
    r = REFERENCE_RANGES["hemoglobin"]
    out = analyze_extracted_values({
        "hemoglobin": _field("hemoglobin", r["low"]),
    })
    assert out["abnormal_values"] == []
    out = analyze_extracted_values({"hemoglobin": _field("hemoglobin", r["high"])})
    assert out["abnormal_values"] == []


def test_unknown_tests_are_ignored():
    out = analyze_extracted_values({"made up": {"value": 1, "unit": "x", "display_name": "Fake"}})
    assert out["abnormal_values"] == [] and out["normal_values"] == []


def test_empty_input_does_not_crash():
    out = analyze_extracted_values({})
    assert out["abnormal_values"] == []


SAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "test-assets", "sample_lab_report.png")


@pytest.mark.skipif(
    not (shutil.which("tesseract") and os.path.exists(SAMPLE)),
    reason="Tesseract or sample image not available",
)
def test_ocr_end_to_end_on_sample_report(client, patient):
    with open(SAMPLE, "rb") as f:
        up = client.post("/v1/reports/upload", headers=patient["headers"],
                         files={"file": ("sample.png", f.read(), "image/png")})
    assert up.status_code == 201
    r = client.post(f"/v1/reports/{up.json()['id']}/analyze", headers=patient["headers"])
    assert r.status_code == 200, r.text
    body = r.json()
    analysis = body.get("analysis", body)
    found = len(analysis["abnormal_values"]) + len(analysis["normal_values"])
    assert found >= 1
