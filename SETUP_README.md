# MedAssist AI — Backend Base Setup (Sprint 1 Deliverable)

This is a working FastAPI + PostgreSQL + Redis base, matching Phase 0 / Sprint 1 of the Development Roadmap. It includes a fully functional **Authentication module** (register, login, refresh) built with the clean architecture layering (`router → service → repository → model`) defined in the Folder Structure doc.

## What's included

- `docker-compose.yml` — spins up Postgres, Redis, and the FastAPI backend
- `backend/app/main.py` — FastAPI entrypoint with `/health` check
- `backend/app/config.py` — environment-based settings
- `backend/app/core/` — security (JWT + Argon2 password hashing), exception handling
- `backend/app/db/` — SQLAlchemy session/engine, declarative base, Redis client
- `backend/app/modules/authentication/` — full register/login/refresh flow:
  - `models.py` — `User` SQLAlchemy model
  - `schemas.py` — Pydantic request/response DTOs with password-strength validation
  - `repository.py` — DB access layer
  - `services.py` — business logic (registration, login, token refresh)
  - `router.py` — `/v1/auth/register`, `/v1/auth/login`, `/v1/auth/refresh`
- `backend/alembic/` — migration tooling wired to the SQLAlchemy models

## How to run it

### 1. Copy this into your repo
Merge the `backend/` folder and `docker-compose.yml` into your existing `medassist-ai` repo (it replaces the empty placeholder files with working code).

### 2. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and set a real `JWT_SECRET_KEY` (never commit real secrets).

### 3. Start everything
```bash
docker-compose up --build
```

### 4. Generate and run the first migration
Once containers are up, in a new terminal:
```bash
docker exec -it medassist-backend alembic revision --autogenerate -m "create users table"
docker exec -it medassist-backend alembic upgrade head
```

### 5. Verify
- Health check: http://localhost:8000/health
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Try `POST /v1/auth/register` with:
```json
{ "email": "test@example.com", "phone": "+911234567890", "password": "Passw0rd!" }
```

> Note: registration currently creates the user with `is_verified = False` (OTP delivery is a `TODO` in `services.py` — wire up an SMS/email provider e.g. Twilio/SES before login will succeed end-to-end). For local testing, you can manually set `is_verified = true` on the row in Postgres.

## Next steps (per Roadmap Phase 1)

Add the remaining backend modules using this exact same pattern — copy the `authentication/` folder structure for each:
- `users`, `patients`, `doctors`, `appointments`, `medical_reports`, `prescriptions`, `notifications`, `chat`, `ai_apis`, `analytics`, `file_upload`, `settings`

Each new module needs:
1. `models.py` → add the import in `alembic/env.py` so migrations pick it up
2. `schemas.py`, `repository.py`, `services.py`, `router.py`
3. Register its router in `app/main.py`: `app.include_router(<module>_router, prefix="/v1")`
