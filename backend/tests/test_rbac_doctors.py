import uuid


def test_patient_cannot_use_doctor_endpoints(client, patient):
    assert client.get("/v1/doctors/me", headers=patient["headers"]).status_code == 403
    assert client.get("/v1/doctors/me/patients", headers=patient["headers"]).status_code == 403


def test_doctor_cannot_use_patient_only_endpoints(client, doctor):
    r = client.post("/v1/ai/health-risk-score", headers=doctor["headers"])
    assert r.status_code == 403


def test_patient_cannot_access_admin_routes(client, patient):
    assert client.get("/v1/admin/users", headers=patient["headers"]).status_code == 403
    assert client.get("/v1/admin/analytics/overview", headers=patient["headers"]).status_code in (403, 404)


def test_admin_can_list_users(client, admin):
    r = client.get("/v1/admin/users", headers=admin["headers"])
    assert r.status_code == 200


def test_doctor_directory_hides_license_number(client, patient, doctor):
    client.put(
        "/v1/doctors/me",
        headers=doctor["headers"],
        json={"full_name": "Dr. Test", "specialization": "Cardiology",
              "license_number": "LIC-12345", "years_experience": 8},
    )
    r = client.get("/v1/doctors", headers=patient["headers"])
    assert r.status_code == 200
    assert any(d["full_name"] == "Dr. Test" for d in r.json())
    assert all("license_number" not in d for d in r.json())


def test_doctor_profile_update_persists(client, doctor):
    r = client.put(
        "/v1/doctors/me",
        headers=doctor["headers"],
        json={"full_name": "Dr. Updated", "specialization": "Neurology",
              "license_number": "LIC-999", "years_experience": 3},
    )
    assert r.status_code == 200
    assert client.get("/v1/doctors/me", headers=doctor["headers"]).json()["full_name"] == "Dr. Updated"


def test_doctor_directory_requires_login(client):
    assert client.get("/v1/doctors").status_code in (401, 403)


def _upload_png(client, headers):
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 64
    return client.post(
        "/v1/reports/upload",
        headers=headers,
        files={"file": ("lab.png", png, "image/png")},
        data={"report_type": "blood_test"},
    )


def test_doctor_needs_assignment_to_view_patient_reports(client, patient, doctor):
    up = _upload_png(client, patient["headers"])
    assert up.status_code == 201, up.text
    report_id = up.json()["id"]
    patient_id = up.json()["patient_id"]

    # not assigned -> forbidden
    assert client.get(f"/v1/reports/{report_id}", headers=doctor["headers"]).status_code == 403
    assert client.get(f"/v1/reports/patient/{patient_id}", headers=doctor["headers"]).status_code == 403

    # assign -> allowed
    a = client.post(f"/v1/doctors/me/patients/{patient_id}/assign", headers=doctor["headers"])
    assert a.status_code == 204
    assert client.get(f"/v1/reports/{report_id}", headers=doctor["headers"]).status_code == 200
    assert client.get(f"/v1/reports/patient/{patient_id}", headers=doctor["headers"]).status_code == 200


def test_patient_cannot_read_another_patients_report(client, make_user):
    p1, p2 = make_user("patient"), make_user("patient")
    report_id = _upload_png(client, p1["headers"]).json()["id"]
    assert client.get(f"/v1/reports/{report_id}", headers=p2["headers"]).status_code == 403


def test_upload_rejects_unsupported_file_type(client, patient):
    r = client.post(
        "/v1/reports/upload",
        headers=patient["headers"],
        files={"file": ("x.exe", b"MZ....", "application/x-msdownload")},
    )
    assert r.status_code in (400, 415, 422)


def test_upload_rejects_empty_file(client, patient):
    r = client.post(
        "/v1/reports/upload",
        headers=patient["headers"],
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert r.status_code in (400, 422)
