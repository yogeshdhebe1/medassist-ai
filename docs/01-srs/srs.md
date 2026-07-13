# MedAssist AI — Software Requirements Specification (SRS)

**Tagline:** AI-Powered Intelligent Healthcare Platform
**Document version:** 1.0
**Status:** Draft for development handoff

---

## 1. Problem Statement

Patients frequently lack timely, accessible guidance to interpret symptoms, understand lab/medical report values, or assess their overall health risk before consulting a doctor. Doctors and hospital administrators, in turn, lack a unified digital system that consolidates patient history, AI-assisted diagnostics, and analytics in one place. Existing healthcare apps are typically single-purpose (appointment booking *or* teleconsultation *or* report storage) and rarely integrate real AI/ML decision support directly into the patient and clinician workflow.

MedAssist AI addresses this gap by combining a patient-facing mobile app, a doctor/admin web dashboard, and a suite of AI/ML microservices (symptom checking, disease prediction, OCR-based report analysis, a RAG-powered chatbot, and personalized recommendations) into a single, secure, and scalable platform.

## 2. Objectives

- Provide patients with instant, AI-assisted preliminary health insights (symptom checking, disease risk prediction, health risk scoring).
- Digitize and automatically interpret medical reports (OCR + NLP-based analysis).
- Give doctors a consolidated view of patient history, reports, and AI-generated risk indicators to support (not replace) clinical decision-making.
- Give administrators visibility into platform usage, AI performance, and user/doctor management.
- Build the platform on a modular, microservice-friendly architecture that can scale independently across mobile, web, backend, and AI layers.

## 3. Scope

**In scope (v1):**
- Patient registration/authentication, profile, dashboard.
- Medical report upload, OCR extraction, and AI analysis.
- AI Symptom Checker, Disease Prediction (diabetes, heart disease, stroke, kidney disease), Health Risk Score.
- AI Health Chatbot (RAG-based).
- Diet & Exercise recommendations.
- Medicine reminders and notifications.
- Doctor dashboard: patient management, report viewing, prescriptions, patient history.
- Admin dashboard: user/doctor management, analytics, AI monitoring.
- Dockerized deployment with CI/CD.

**Out of scope (v1, planned for future):**
- Hospital, laboratory, and insurance-entity integrations.
- Wearable device integration.
- Voice assistant.
- Multilingual support.
- Full telemedicine (video consultation).

> MedAssist AI is a **clinical decision-support and patient-engagement tool** — it does not provide medical diagnoses and does not replace licensed medical professionals. All AI outputs are advisory and must be flagged as such in the product UI.

## 4. Project Goals

| Goal | Description |
|---|---|
| G1 | Reduce time-to-insight for patients reviewing symptoms or reports |
| G2 | Improve doctor efficiency via consolidated, AI-augmented patient views |
| G3 | Maintain a modular architecture that supports adding new AI modules without re-architecting the platform |
| G4 | Achieve production-grade security and compliance posture for health data |
| G5 | Enable data-driven platform improvement via analytics and AI monitoring |

## 5. Target Users

- **Patients** — primary consumers of the mobile app; general public, varying digital literacy.
- **Doctors** — verified medical professionals using the web dashboard to manage assigned patients.
- **Admins** — internal platform operators managing users, doctors, and system health.
- **Future personas** — Hospitals, Laboratories, Insurance providers (B2B integrations).

## 6. Functional Requirements

### 6.1 Patient
| ID | Requirement |
|---|---|
| FR-P1 | User can register/login via email+password or OTP |
| FR-P2 | User can view and edit their profile and medical history |
| FR-P3 | User can upload medical reports (PDF/image) |
| FR-P4 | System extracts and displays structured values from uploaded reports (OCR) |
| FR-P5 | User can run the AI Symptom Checker by entering free-text or selected symptoms |
| FR-P6 | User can request disease-risk predictions (diabetes, heart, stroke, kidney) by submitting relevant clinical inputs |
| FR-P7 | User can view an aggregated Health Risk Score |
| FR-P8 | User can chat with the AI Health Chatbot about symptoms, reports, or general medical questions |
| FR-P9 | User receives diet and exercise recommendations personalized to their profile |
| FR-P10 | User can set medicine reminders and receive notifications |
| FR-P11 | User can view historical reports and past AI predictions |

### 6.2 Doctor
| ID | Requirement |
|---|---|
| FR-D1 | Doctor can log in and view a dashboard of assigned patients |
| FR-D2 | Doctor can view a patient's uploaded reports and AI-generated summaries |
| FR-D3 | Doctor can view a patient's AI risk scores and prediction history |
| FR-D4 | Doctor can create/update prescriptions for a patient |
| FR-D5 | Doctor can view full patient history in a chronological timeline |

### 6.3 Admin
| ID | Requirement |
|---|---|
| FR-A1 | Admin can manage (create/suspend/delete) patient and doctor accounts |
| FR-A2 | Admin can view platform-wide analytics (usage, predictions issued, report volume) |
| FR-A3 | Admin can monitor AI model health (latency, error rate, drift indicators) |
| FR-A4 | Admin can generate and export operational reports |

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | API p95 response time < 500ms for non-AI endpoints; AI inference endpoints < 3s p95 |
| Scalability | Each AI module deployable/scalable independently; backend horizontally scalable behind a load balancer |
| Availability | Target 99.5% uptime for core services |
| Security | All PHI encrypted at rest and in transit (TLS 1.2+, AES-256); JWT-based auth with RBAC |
| Compliance | Design aligned with HIPAA-style safeguards (access logging, data minimization, consent tracking) — final legal compliance certification is out of scope for engineering and owned by legal/compliance |
| Usability | Mobile app must support offline viewing of previously loaded reports |
| Maintainability | Modular monorepo structure; each module independently testable |
| Observability | Centralized logging, request tracing, and AI model monitoring dashboards |
| Portability | Fully containerized (Docker) for consistent dev/staging/prod parity |
| Auditability | All PHI access and AI predictions logged with timestamp, user, and outcome for audit trail |

## 8. Assumptions

- Users have internet connectivity for real-time AI inference (offline mode limited to cached/read-only data).
- Doctors are pre-verified/onboarded through an admin-controlled process (no public doctor self-signup in v1).
- AI models are advisory; final clinical decisions remain with licensed doctors.
- Initial deployment targets a single-region cloud environment (AWS), with multi-region as future scope.

## 9. Constraints

- Must use the specified technology stack (Flutter, React, FastAPI, PostgreSQL, Redis, Docker).
- AI models must be explainable enough to support a "why this result" summary shown to patients (no fully black-box output without justification text).
- Regulatory constraints around storage/processing of health data apply and must be revisited with legal counsel before production launch in any specific jurisdiction.

## 10. Technology Stack Summary

| Layer | Technology |
|---|---|
| Mobile | Flutter |
| Web Dashboard | React.js |
| Backend | FastAPI (Python) |
| Relational DB | PostgreSQL |
| Cache / Session store | Redis |
| Classical ML | Scikit-learn, XGBoost, LightGBM |
| Deep Learning / NLP | TensorFlow, PyTorch, Hugging Face Transformers |
| OCR | PaddleOCR |
| Vector Search | FAISS |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Cloud | AWS |

## 11. Future Scope

- Wearable device data ingestion (Apple Health, Google Fit, Fitbit).
- Voice assistant interface for symptom checking.
- Multilingual UI and NLP models.
- Hospital and laboratory system integrations (HL7/FHIR).
- Insurance provider integrations for claims support.
- Full telemedicine module (video consults, e-prescriptions to pharmacy).
- Predictive population-health analytics for admins/hospitals.

## 12. Success Metrics

| Metric | Target (post-launch, 6 months) |
|---|---|
| Monthly Active Patients | Baseline + 20% MoM growth |
| Symptom Checker completion rate | > 70% of started sessions completed |
| OCR extraction accuracy | > 90% field-level accuracy on standard lab reports |
| Disease prediction model AUC | > 0.85 on held-out validation set per model |
| Doctor dashboard adoption | > 80% of onboarded doctors active weekly |
| Chatbot resolution rate (no escalation needed) | > 60% |
| Platform uptime | ≥ 99.5% |
| Mean AI inference latency | < 3s p95 |
