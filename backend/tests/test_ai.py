import pytest

DIABETES_HIGH = {"pregnancies": 6, "glucose": 190, "blood_pressure": 90, "skin_thickness": 35,
                 "insulin": 250, "bmi": 38.0, "diabetes_pedigree": 1.2, "age": 55}
DIABETES_LOW = {"pregnancies": 0, "glucose": 85, "blood_pressure": 70, "skin_thickness": 20,
                "insulin": 80, "bmi": 22.0, "diabetes_pedigree": 0.2, "age": 22}


def _prob(resp_json):
    return resp_json.get("probability", resp_json.get("confidence_score"))


def test_diabetes_requires_patient_login(client):
    assert client.post("/v1/ai/disease-prediction/diabetes", json=DIABETES_HIGH).status_code in (401, 403)


def test_diabetes_high_risk_scores_above_low_risk(client, patient):
    hi = client.post("/v1/ai/disease-prediction/diabetes", headers=patient["headers"], json=DIABETES_HIGH)
    lo = client.post("/v1/ai/disease-prediction/diabetes", headers=patient["headers"], json=DIABETES_LOW)
    assert hi.status_code == 200, hi.text
    assert lo.status_code == 200, lo.text
    p_hi, p_lo = _prob(hi.json()), _prob(lo.json())
    assert p_hi is not None and p_lo is not None
    assert 0 <= p_lo < p_hi <= 1


def test_diabetes_validates_ranges(client, patient):
    bad = {**DIABETES_LOW, "pregnancies": 99}
    r = client.post("/v1/ai/disease-prediction/diabetes", headers=patient["headers"], json=bad)
    assert r.status_code == 422


def test_prediction_is_saved_to_history(client, patient):
    client.post("/v1/ai/disease-prediction/diabetes", headers=patient["headers"], json=DIABETES_LOW)
    r = client.get("/v1/ai/predictions/history", headers=patient["headers"])
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_symptom_checker_returns_ranked_predictions(client, patient):
    known = client.get("/v1/ai/symptom-checker/symptoms", headers=patient["headers"]).json()
    symptoms = known["symptoms"] if isinstance(known, dict) else known
    assert len(symptoms) > 10
    r = client.post("/v1/ai/symptom-checker", headers=patient["headers"], json={"symptoms": symptoms[:3]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["predictions"]
    assert body["recognized_symptoms"]


def test_symptom_checker_rejects_empty_list(client, patient):
    r = client.post("/v1/ai/symptom-checker", headers=patient["headers"], json={"symptoms": []})
    assert r.status_code == 422


def test_health_risk_score_needs_a_prediction_first(client, patient):
    r = client.post("/v1/ai/health-risk-score", headers=patient["headers"])
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "NO_PREDICTIONS_AVAILABLE"


def test_health_risk_score_single_component_equals_that_component(client, patient):
    d = client.post("/v1/ai/disease-prediction/diabetes", headers=patient["headers"], json=DIABETES_HIGH).json()
    r = client.post("/v1/ai/health-risk-score", headers=patient["headers"])
    assert r.status_code == 200, r.text
    body = r.json()
    # one component: 0.7*x + 0.3*x == x
    assert body["overall_score"] == pytest.approx(round(_prob(d) * 100, 1), abs=0.11)
    assert body["components_available"] == ["metabolic"]
    assert body["trend"] == "first_calculation"


def test_blend_formula_prevents_masking_by_average():
    from app.modules.ai_apis.service_risk_score import WORST_WEIGHT, AVERAGE_WEIGHT

    values = [93.6, 5.0, 4.0, 3.0]
    blended = WORST_WEIGHT * max(values) + AVERAGE_WEIGHT * (sum(values) / len(values))
    assert blended > sum(values) / len(values) * 2  # far above the plain mean (26.4)
    assert WORST_WEIGHT + AVERAGE_WEIGHT == pytest.approx(1.0)


@pytest.mark.parametrize("path", ["diet", "exercise"])
def test_recommendations_endpoints_work(client, patient, path):
    r = client.post(f"/v1/ai/recommendations/{path}", headers=patient["headers"], json={})
    assert r.status_code == 200, r.text
