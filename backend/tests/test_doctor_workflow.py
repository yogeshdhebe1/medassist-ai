from tests.conftest import future_iso


def _book(client, patient, doctor):
    r = client.post(
        "/v1/appointments",
        headers=patient["headers"],
        json={"doctor_id": doctor["doctor_id"], "scheduled_at": future_iso(), "reason": "Chest pain"},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_doctor_sees_patient_name_on_appointments(client, patient, doctor):
    client.put("/v1/patients/me", headers=patient["headers"], json={"full_name": "Asha Patil"})
    _book(client, patient, doctor)
    rows = client.get("/v1/appointments", headers=doctor["headers"]).json()
    assert len(rows) == 1
    assert rows[0]["patient_name"] == "Asha Patil"


def test_confirming_appointment_assigns_patient(client, patient, doctor):
    assert client.get("/v1/doctors/me/patients", headers=doctor["headers"]).json() == []
    appt_id = _book(client, patient, doctor)
    r = client.patch(f"/v1/appointments/{appt_id}/status", headers=doctor["headers"], json={"status": "confirmed"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "confirmed"
    assigned = client.get("/v1/doctors/me/patients", headers=doctor["headers"]).json()
    assert len(assigned) == 1


def test_doctor_cannot_change_another_doctors_appointment(client, patient, doctor, make_user):
    appt_id = _book(client, patient, doctor)
    other = make_user("doctor")
    client.get("/v1/doctors/me", headers=other["headers"])
    r = client.patch(f"/v1/appointments/{appt_id}/status", headers=other["headers"], json={"status": "confirmed"})
    assert r.status_code == 403


def test_notes_require_assignment_then_work(client, patient, doctor):
    appt_id = _book(client, patient, doctor)
    # not yet assigned: need the patient id -> read it via the patient's own profile
    patient_id = client.get("/v1/patients/me", headers=patient["headers"]).json()["id"]
    blocked = client.post("/v1/doctors/me/patient-notes", headers=doctor["headers"],
                          json={"patient_id": patient_id, "note": "hello"})
    assert blocked.status_code == 403
    assert client.get(f"/v1/doctors/me/patients/{patient_id}/notes", headers=doctor["headers"]).status_code == 403

    client.patch(f"/v1/appointments/{appt_id}/status", headers=doctor["headers"], json={"status": "confirmed"})
    ok = client.post("/v1/doctors/me/patient-notes", headers=doctor["headers"],
                     json={"patient_id": patient_id, "note": "Advise ECG"})
    assert ok.status_code == 201
    notes = client.get(f"/v1/doctors/me/patients/{patient_id}/notes", headers=doctor["headers"]).json()
    assert [n["note"] for n in notes] == ["Advise ECG"]


def test_empty_note_rejected(client, patient, doctor):
    appt_id = _book(client, patient, doctor)
    patient_id = client.get("/v1/patients/me", headers=patient["headers"]).json()["id"]
    client.patch(f"/v1/appointments/{appt_id}/status", headers=doctor["headers"], json={"status": "confirmed"})
    r = client.post("/v1/doctors/me/patient-notes", headers=doctor["headers"],
                    json={"patient_id": patient_id, "note": "   "})
    assert r.status_code == 422
