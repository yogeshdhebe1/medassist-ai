# Notifications Module — Update Package

Adds in-app notifications, plus something more interesting: a reusable `NotificationService.notify()` helper that **other modules call as a side effect of their own actions** — this is the first bit of cross-module, event-driven behavior in the codebase (previously every module only touched its own data).

## What's new

- `app/modules/notifications/` — full module (model, schemas, repository, service, router)
- `app/modules/appointments/services.py` — **modified**: now sends a notification to the doctor when a patient books, and to the patient when the doctor confirms
- `app/modules/prescriptions/services.py` — **modified**: now sends a notification to the patient when a doctor issues a prescription
- `app/main.py`, `alembic/env.py` — **modified**: register the new router/model

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/v1/notifications` | Bearer (any role) | List your notifications (supports `?unread_only=true`) |
| GET | `/v1/notifications/unread-count` | Bearer (any role) | Get just the unread count (for a UI badge) |
| PATCH | `/v1/notifications/{notification_id}/read` | Bearer (owner only) | Mark a notification as read |

## How to apply

1. Copy `backend/` content into your repo's `backend/`:
   - Add the new `app/modules/notifications/` folder
   - **Overwrite** `app/modules/appointments/services.py` and `app/modules/prescriptions/services.py` (these now call the notification service)
   - Overwrite `app/main.py` and `alembic/env.py`
2. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "create notifications table"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

The easiest way to test this is to **re-run actions from earlier modules** and watch notifications appear as a side effect:

1. **As patient**: book a new appointment (`POST /v1/appointments`) with any doctor.
2. **Switch to doctor token**: `GET /v1/notifications` → you should see a `"appointment_requested"` notification.
3. **As doctor**: confirm that appointment (`PATCH /v1/appointments/{id}/status` → `"confirmed"`).
4. **Switch to patient token**: `GET /v1/notifications` → you should see a `"appointment_confirmed"` notification.
5. **As doctor**: issue a prescription for that patient (`POST /v1/prescriptions`).
6. **As patient**: `GET /v1/notifications` → a `"prescription_issued"` notification should now also appear.
7. `GET /v1/notifications/unread-count` → should show the count of unread notifications.
8. `PATCH /v1/notifications/{notification_id}/read` on one of them → then check `unread-count` again, it should have decreased by 1.
9. **RBAC test**: try marking a notification that belongs to a *different* user (copy an ID from the other role's list) → should get 403.

## Design notes

- **`notify()` as a cross-module contract**: rather than each module writing directly to the `notifications` table, they all go through `NotificationService.notify(user_id, title, body, type)`. This is the same principle as the `_assert_assigned` RBAC check being centralized in one place — one method owns "how a notification gets created," so if you later swap this for real push notifications (FCM) or email, there's exactly one place to change.
- **This is the first genuinely cross-module dependency** in the codebase (`appointments` and `prescriptions` now import from `notifications`). It's worth being able to explain in an interview why this doesn't create a circular import problem: `notifications` doesn't import anything from `appointments` or `prescriptions` — dependencies only flow one direction.
- **`type` field is a free-form string** (not an enum) deliberately — new notification types (e.g. `report_analyzed` once the OCR module exists, `medicine_reminder`) can be added by any future module without a schema migration.
