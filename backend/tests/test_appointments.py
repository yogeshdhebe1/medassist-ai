import uuid

from tests.conftest import future_iso, past_iso


def test_book_future_appointment(client, patient, doctor):
    r = client.post(
        "/v1/appointments",
        headers=patient["headers"],
        json={"doctor_id": doctor["doctor_id"], "scheduled_at": future_iso(), "reason": "Checkup"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "scheduled" or r.json()["status"]
    assert r.json()["reason"] == "Checkup"


def test_past_appointment_rejected(client, patient, doctor):
    r = client.post(
        "/v1/appointments",
        headers=patient["headers"],
        json={"doctor_id": doctor["doctor_id"], "scheduled_at": past_iso()},
    )
    assert r.status_code == 422


def test_unknown_doctor_not_found(client, patient):
    r = client.post(
        "/v1/appointments",
        headers=patient["headers"],
        json={"doctor_id": str(uuid.uuid4()), "scheduled_at": future_iso()},
    )
    assert r.status_code == 404


def test_invalid_doctor_id_is_422(client, patient):
    r = client.post(
        "/v1/appointments",
        headers=patient["headers"],
        json={"doctor_id": "not-a-uuid", "scheduled_at": future_iso()},
    )
    assert r.status_code == 422


def test_reason_too_long_rejected(client, patient, doctor):
    r = client.post(
        "/v1/appointments",
        headers=patient["headers"],
        json={"doctor_id": doctor["doctor_id"], "scheduled_at": future_iso(), "reason": "x" * 501},
    )
    assert r.status_code == 422


def test_patients_only_see_their_own_appointments(client, make_user, doctor):
    p1, p2 = make_user("patient"), make_user("patient")
    client.post("/v1/appointments", headers=p1["headers"],
                json={"doctor_id": doctor["doctor_id"], "scheduled_at": future_iso()})
    assert len(client.get("/v1/appointments", headers=p1["headers"]).json()) == 1
    assert client.get("/v1/appointments", headers=p2["headers"]).json() == []
