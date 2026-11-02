import uuid

from tests.conftest import PASSWORD, _make_user


def _payload(**over):
    base = {
        "email": f"u-{uuid.uuid4().hex[:6]}@example.com",
        "phone": "9" + str(uuid.uuid4().int)[:9],
        "password": PASSWORD,
    }
    base.update(over)
    return base


def test_register_creates_patient(client):
    r = client.post("/v1/auth/register", json=_payload())
    assert r.status_code == 201
    assert "user_id" in r.json()


def test_register_rejects_weak_password(client):
    for bad in ["short1!", "nodigits!!", "NoSymbol123"]:
        r = client.post("/v1/auth/register", json=_payload(password=bad))
        assert r.status_code == 422, bad


def test_register_duplicate_email_conflicts(client):
    p = _payload()
    assert client.post("/v1/auth/register", json=p).status_code == 201
    again = _payload(email=p["email"])
    assert client.post("/v1/auth/register", json=again).status_code == 409


def test_login_blocked_until_verified(client):
    u = _make_user(client, "patient", verified=False)
    r = client.post("/v1/auth/login", json={"email": u["email"], "password": PASSWORD})
    assert r.status_code == 403


def test_login_wrong_password(client):
    u = _make_user(client, "patient")
    r = client.post("/v1/auth/login", json={"email": u["email"], "password": "Wrong!123"})
    assert r.status_code == 401
    assert r.json()["error"]["code"]


def test_login_returns_tokens_and_role(client):
    u = _make_user(client, "doctor")
    r = client.post("/v1/auth/login", json={"email": u["email"], "password": PASSWORD})
    body = r.json()
    assert r.status_code == 200
    assert body["role"] == "doctor"
    assert body["access_token"] and body["refresh_token"]


def test_refresh_issues_new_access_token(client):
    u = _make_user(client, "patient")
    tokens = client.post("/v1/auth/login", json={"email": u["email"], "password": PASSWORD}).json()
    r = client.post("/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_access_token_cannot_be_used_as_refresh_token(client):
    u = _make_user(client, "patient")
    tokens = client.post("/v1/auth/login", json={"email": u["email"], "password": PASSWORD}).json()
    r = client.post("/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r.status_code == 401


def test_protected_route_needs_token(client):
    assert client.get("/v1/doctors").status_code in (401, 403)
    assert client.get("/v1/patients/me").status_code in (401, 403)


def test_garbage_token_rejected(client):
    r = client.get("/v1/patients/me", headers={"Authorization": "Bearer not.a.token"})
    assert r.status_code == 401
