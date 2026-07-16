# Final 3 Modules — Users, Settings, Chat

This update completes **all 13 originally planned backend modules**. `users` and `settings` add no new database tables of significant complexity; `chat` adds two new tables (`chat_sessions`, `chat_messages`).

---

## 1. Users (Admin) — `/v1/admin/users`

Admin-facing user management, separate from the auth-flow-specific `UserRepository` in the `authentication` module.

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/v1/admin/users` | Bearer (role: admin) | List/search/filter all users (`?role=`, `?is_active=`, `?search=`) |
| PATCH | `/v1/admin/users/{user_id}/status` | Bearer (role: admin) | Activate/deactivate a user account |

**Notable guardrail**: an admin cannot deactivate their own account via this endpoint (`SelfLockoutError`, 400) — a real safety concern worth having for any admin-management feature, and a good detail to mention if asked about edge cases you considered.

## 2. Settings — `/v1/settings`

Per-user preferences (notifications, language, theme), same lazy-creation pattern as `patients`/`doctors` profiles.

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/v1/settings/me` | Bearer (any role) | Get your settings (auto-creates defaults on first call) |
| PUT | `/v1/settings/me` | Bearer (any role) | Update settings (partial updates supported) |

## 3. Chat (AI Health Chatbot) — `/v1/chat`

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/chat/sessions` | Bearer (role: patient) | Start a new chat session |
| POST | `/v1/chat/sessions/{session_id}/messages` | Bearer (owner patient) | Send a message, get a reply |
| GET | `/v1/chat/sessions/{session_id}/messages` | Bearer (owner patient) | View message history |

**Important honesty point for your resume/interview**: this chatbot is **keyword-matching, not a real LLM/RAG pipeline**. The AI Pipeline doc describes the "real" version as FAISS retrieval + an LLM — that requires external API keys and a vector database, which is out of scope for a resume project without ongoing hosting costs. What's built here is deliberately structured so that swapping in real RAG later only touches `bot_engine.py`'s `generate_reply()` function — sessions, message persistence, and the API contract don't change. **Be upfront about this distinction if asked** — claiming a keyword-matcher is "AI-powered NLP" would be a credibility risk in an interview; describing it accurately as "a rule-based chatbot architected to be RAG-upgradeable" is honest and still shows good design thinking.

## How to apply

1. Copy `backend/app/modules/{users,settings,chat}/` into your repo, overwrite `app/main.py` and `alembic/env.py`.
2. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "add settings, chat, and finalize users module"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

**Users (admin)**:
1. As admin: `GET /v1/admin/users` → should list all your test users (patient, doctor, admin).
2. Try `PATCH /v1/admin/users/{your_own_admin_user_id}/status` with `{"is_active": false}` → should get 400 `SELF_LOCKOUT`.
3. Try it on a different user's ID → should succeed.

**Settings**:
1. As any logged-in user: `GET /v1/settings/me` → defaults auto-created.
2. `PUT /v1/settings/me` with `{"theme": "dark", "language": "hi"}` → partial update, other fields unchanged.

**Chat**:
1. As patient: `POST /v1/chat/sessions` → get a `session_id`.
2. `POST /v1/chat/sessions/{session_id}/messages` with `{"message": "I have a fever, what should I do?"}` → should get a relevant canned reply + disclaimer.
3. Try `{"message": "tell me about diabetes"}` → different, topic-relevant reply.
4. `GET /v1/chat/sessions/{session_id}/messages` → both your message and the bot's replies should appear, in order.
5. **RBAC test**: try accessing someone else's `session_id` → 403.

---

## 🎉 All 13 backend modules complete

| # | Module | 
|---|---|
| 1 | Authentication |
| 2 | Users (Admin) |
| 3 | Patients |
| 4 | Doctors |
| 5 | Appointments |
| 6 | Medical Reports |
| 7 | Prescriptions |
| 8 | Notifications |
| 9 | Chat |
| 10 | AI APIs (Diabetes Prediction) |
| 11 | Analytics |
| 12 | File Upload (covered within Medical Reports) |
| 13 | Settings |
