# MedAssist AI — REST API Design

Base URL: `https://api.medassist.ai/v1`
Format: JSON over HTTPS. Auth: Bearer JWT (unless noted). All timestamps ISO-8601 UTC.

Standard error envelope:
```json
{ "error": { "code": "STRING_CODE", "message": "Human readable", "details": {} } }
```

---

## 1. Authentication APIs

### POST /auth/register
| | |
|---|---|
| Auth | None |
| Request | `{ "email": string, "phone": string, "password": string, "role": "patient" }` |
| Response 201 | `{ "user_id": uuid, "message": "Verification OTP sent" }` |
| Validation | Email format, password ≥ 8 chars with 1 number + 1 symbol, phone E.164 format, role restricted to `patient` (doctor/admin created via admin-only flow) |
| Status Codes | 201 Created, 400 Validation Error, 409 Email/Phone already exists |

### POST /auth/verify-otp
| | |
|---|---|
| Auth | None |
| Request | `{ "user_id": uuid, "otp": string }` |
| Response 200 | `{ "message": "Verified" }` |
| Status Codes | 200, 400 Invalid OTP, 410 OTP Expired |

### POST /auth/login
| | |
|---|---|
| Auth | None |
| Request | `{ "email": string, "password": string }` |
| Response 200 | `{ "access_token": string, "refresh_token": string, "expires_in": int, "role": string }` |
| Status Codes | 200, 401 Invalid Credentials, 403 Account Not Verified |

### POST /auth/refresh
| | |
|---|---|
| Auth | Refresh token (body) |
| Request | `{ "refresh_token": string }` |
| Response 200 | `{ "access_token": string, "expires_in": int }` |
| Status Codes | 200, 401 Invalid/Expired Refresh Token |

### POST /auth/logout
| | |
|---|---|
| Auth | Bearer |
| Response 200 | `{ "message": "Logged out" }` |
| Status Codes | 200, 401 |

---

## 2. Patient APIs

### GET /patients/me
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Response 200 | Full patient profile object |
| Status Codes | 200, 401, 404 |

### PUT /patients/me
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Request | `{ "full_name": string, "date_of_birth": date, "gender": string, "height_cm": float, "weight_kg": float, "blood_group": string, "medical_history": object }` |
| Response 200 | Updated profile object |
| Validation | height/weight positive floats within physiologically plausible ranges; date_of_birth in the past |
| Status Codes | 200, 400, 401 |

### GET /patients/{patient_id}/history
| | |
|---|---|
| Auth | Bearer (role: doctor with active assignment, or admin, or the patient themself) |
| Response 200 | `{ "reports": [...], "predictions": [...], "prescriptions": [...] }` |
| Status Codes | 200, 401, 403 Forbidden (not assigned doctor), 404 |

---

## 3. Doctor APIs

### GET /doctors/me/patients
| | |
|---|---|
| Auth | Bearer (role: doctor) |
| Query params | `page`, `page_size`, `search` |
| Response 200 | Paginated list of assigned patients (summary view) |
| Status Codes | 200, 401 |

### GET /doctors/{doctor_id}
| | |
|---|---|
| Auth | Bearer |
| Response 200 | Doctor public profile (specialization, experience, rating) |
| Status Codes | 200, 404 |

### POST /doctors/{doctor_id}/patient-notes
| | |
|---|---|
| Auth | Bearer (role: doctor, must be assigned to patient) |
| Request | `{ "patient_id": uuid, "note": string }` |
| Response 201 | Created note object |
| Status Codes | 201, 400, 403 |

---

## 4. Medical Report APIs

### POST /reports/upload
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Request | `multipart/form-data` — `file` (PDF/JPG/PNG, max 15MB), `report_type` |
| Response 202 | `{ "report_id": uuid, "status": "processing" }` (async OCR + analysis pipeline) |
| Validation | MIME type whitelist, file size limit, virus/malware scan pre-storage |
| Status Codes | 202 Accepted, 400 Invalid File, 413 Payload Too Large, 401 |

### GET /reports/{report_id}
| | |
|---|---|
| Auth | Bearer (owner patient, assigned doctor, or admin) |
| Response 200 | `{ "report": {...}, "ocr_result": {...}, "analysis": {...}, "status": "completed" \| "processing" \| "failed" }` |
| Status Codes | 200, 401, 403, 404 |

### GET /reports
| | |
|---|---|
| Auth | Bearer (role: patient — own reports; doctor — assigned patients via `patient_id` query) |
| Query params | `patient_id` (doctor only), `page`, `page_size`, `report_type` |
| Response 200 | Paginated report list |
| Status Codes | 200, 401, 403 |

---

## 5. AI Prediction APIs

### POST /ai/symptom-checker
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Request | `{ "symptoms_text": string, "duration_days": int, "severity": "mild"\|"moderate"\|"severe" }` |
| Response 200 | `{ "predictions": [ { "disease": string, "confidence": float, "explanation": string } ], "recommend_doctor_visit": bool }` |
| Validation | `symptoms_text` non-empty, ≤ 2000 chars |
| Status Codes | 200, 400, 401, 503 AI Service Unavailable |

### POST /ai/disease-prediction/{disease_type}
`disease_type ∈ { diabetes, heart-disease, stroke, kidney-disease }`
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Request | Disease-specific structured clinical inputs, e.g. diabetes: `{ "glucose": float, "bmi": float, "age": int, "blood_pressure": float, ... }` |
| Response 200 | `{ "risk_level": "low"\|"medium"\|"high", "probability": float, "contributing_factors": [string], "model_version": string }` |
| Validation | All fields required, numeric ranges validated per clinical plausibility |
| Status Codes | 200, 400, 401, 503 |

### POST /ai/health-risk-score
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Response 200 | `{ "overall_score": float, "component_scores": { "cardiac": float, "metabolic": float, "renal": float }, "trend": "improving"\|"stable"\|"worsening" }` |
| Status Codes | 200, 401, 503 |

### GET /ai/predictions/history
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Query params | `prediction_type`, `from`, `to`, `page` |
| Response 200 | Paginated prediction history |
| Status Codes | 200, 401 |

### POST /ai/recommendations/diet
### POST /ai/recommendations/exercise
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Request | `{}` (uses stored profile) or optional overrides `{ "goal": "weight_loss"\|"maintenance"\|"muscle_gain" }` |
| Response 200 | `{ "plan": [...], "rationale": string }` |
| Status Codes | 200, 401, 503 |

---

## 6. Chatbot APIs

### POST /chat/sessions
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Response 201 | `{ "session_id": uuid }` |
| Status Codes | 201, 401 |

### POST /chat/sessions/{session_id}/messages
| | |
|---|---|
| Auth | Bearer (role: patient, owner of session) |
| Request | `{ "message": string }` |
| Response 200 | `{ "reply": string, "sources": [string], "disclaimer": string }` |
| Validation | message ≤ 1000 chars, rate-limited to N messages/min per user |
| Status Codes | 200, 400, 401, 403, 429 Too Many Requests, 503 |

### GET /chat/sessions/{session_id}/messages
| | |
|---|---|
| Auth | Bearer (owner) |
| Response 200 | Paginated message history |
| Status Codes | 200, 401, 403 |

---

## 7. Prescription APIs

### POST /prescriptions
| | |
|---|---|
| Auth | Bearer (role: doctor) |
| Request | `{ "patient_id": uuid, "medications": [ { "name": string, "dosage": string, "frequency": string, "duration_days": int } ], "notes": string }` |
| Response 201 | Created prescription object |
| Status Codes | 201, 400, 403 (not assigned doctor) |

### GET /prescriptions/{patient_id}
| | |
|---|---|
| Auth | Bearer (owner patient, assigned doctor, admin) |
| Response 200 | List of prescriptions, newest first |
| Status Codes | 200, 401, 403 |

---

## 8. Notification APIs

### GET /notifications
| | |
|---|---|
| Auth | Bearer |
| Query params | `unread_only`, `page` |
| Response 200 | Paginated notifications |
| Status Codes | 200, 401 |

### PATCH /notifications/{id}/read
| | |
|---|---|
| Auth | Bearer (owner) |
| Response 200 | `{ "message": "marked read" }` |
| Status Codes | 200, 401, 404 |

### POST /reminders/medicine
| | |
|---|---|
| Auth | Bearer (role: patient) |
| Request | `{ "medicine_name": string, "dosage": string, "schedule_cron": string }` |
| Response 201 | Created reminder |
| Status Codes | 201, 400, 401 |

---

## 9. Analytics APIs (Admin)

### GET /admin/analytics/overview
| | |
|---|---|
| Auth | Bearer (role: admin) |
| Response 200 | `{ "total_patients": int, "total_doctors": int, "reports_processed_30d": int, "predictions_issued_30d": int }` |
| Status Codes | 200, 401, 403 |

### GET /admin/analytics/ai-monitoring
| | |
|---|---|
| Auth | Bearer (role: admin) |
| Response 200 | Per-model latency, error rate, request volume, drift flag |
| Status Codes | 200, 401, 403 |

### GET /admin/users
| | |
|---|---|
| Auth | Bearer (role: admin) |
| Query params | `role`, `status`, `page`, `search` |
| Response 200 | Paginated user list |
| Status Codes | 200, 401, 403 |

### PATCH /admin/users/{user_id}/status
| | |
|---|---|
| Auth | Bearer (role: admin) |
| Request | `{ "is_active": bool }` |
| Response 200 | Updated user object |
| Status Codes | 200, 401, 403, 404 |

---

## 10. Global Conventions

| Aspect | Convention |
|---|---|
| Pagination | `page` (1-indexed), `page_size` (default 20, max 100); response includes `total`, `page`, `page_size` |
| Auth header | `Authorization: Bearer <JWT>` |
| Rate limiting | Per-user token bucket via Redis; AI endpoints stricter limits than CRUD endpoints |
| Idempotency | `POST` endpoints that trigger AI jobs accept optional `Idempotency-Key` header to avoid duplicate job submission on retry |
| Versioning | URI-based (`/v1`); breaking changes ship as `/v2` with a deprecation window |
| Validation errors | 400 responses include field-level error details in `error.details` |
