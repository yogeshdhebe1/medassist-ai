# MedAssist AI — Production-Ready Project Structure

A monorepo-style, enterprise-grade folder architecture for an AI-powered healthcare platform comprising a Flutter patient app, a React doctor/admin dashboard, a FastAPI backend, a suite of independent AI/ML modules, PostgreSQL/Redis data layer, and Docker-based deployment.

---

## 1. Top-Level Layout

```
medassist-ai/
├── mobile-app/              # Flutter patient application
├── web-dashboard/           # React doctor & admin dashboard
├── backend/                 # FastAPI backend (core API)
├── ai-services/             # All AI/ML modules (independent microservices)
├── database/                # PostgreSQL & Redis schemas, migrations, seeds
├── deployment/              # Docker, Nginx, CI/CD, Terraform, K8s, AWS
├── docs/                    # All project documentation
├── tests/                   # Cross-cutting test suites
├── scripts/                 # DevOps & automation scripts
├── .github/                 # GitHub Actions workflows & templates
├── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── LICENSE
└── README.md
```

**Purpose:** Each top-level folder is an independently deployable/ownable unit. This allows separate teams (mobile, web, backend, AI, DevOps) to work in isolation while sharing a common docs/testing/deployment backbone — a common pattern for scaling engineering orgs around a single product.

---

## 2. Backend — `backend/` (FastAPI, Clean Architecture)

```
backend/
├── app/
│   ├── main.py                        # FastAPI app entrypoint
│   ├── config.py                      # Settings (env, secrets, constants)
│   ├── dependencies.py                # Shared DI providers (DB session, auth, etc.)
│   │
│   ├── core/                          # Cross-cutting core concerns
│   │   ├── security.py                # JWT, OAuth2, password hashing
│   │   ├── exceptions.py              # Global exception classes & handlers
│   │   ├── logging.py                 # Structured logging setup
│   │   ├── middleware.py              # CORS, rate-limiting, request logging
│   │   ├── pagination.py
│   │   └── constants.py
│   │
│   ├── db/
│   │   ├── base.py                    # SQLAlchemy Base + model registry
│   │   ├── session.py                 # DB session/engine factory
│   │   ├── redis_client.py
│   │   └── init_db.py
│   │
│   └── modules/                       # Feature modules (see 2.1 below)
│       ├── authentication/
│       ├── users/
│       ├── patients/
│       ├── doctors/
│       ├── appointments/
│       ├── medical_reports/
│       ├── prescriptions/
│       ├── notifications/
│       ├── chat/
│       ├── ai_apis/
│       ├── analytics/
│       ├── file_upload/
│       └── settings/
│
├── alembic/                           # DB migrations
│   ├── versions/
│   └── env.py
│
├── tests/                             # Backend-specific tests (mirrors modules/)
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── Dockerfile
├── alembic.ini
├── pyproject.toml
└── pytest.ini
```

### 2.1 Standard Module Blueprint (applied to every module above)

Each of the 13 backend modules follows this identical internal structure — this consistency is what makes the codebase predictable and easy to onboard new engineers into:

```
modules/<module_name>/
├── __init__.py
├── models.py            # SQLAlchemy ORM models (DB tables)
├── schemas.py           # Pydantic request/response DTOs
├── router.py            # FastAPI route definitions (HTTP layer only)
├── services.py          # Business logic / use cases
├── repository.py        # DB access layer (queries, isolated from business logic)
├── utils.py             # Module-scoped helpers
├── exceptions.py        # Module-specific exceptions
└── dependencies.py      # Module-scoped DI (permissions, validators)
```

**Purpose:** Enforces Clean Architecture separation — `router` (interface) → `service` (domain logic) → `repository` (data access) → `models` (persistence). This keeps business logic testable independent of FastAPI or the database, and lets any module be extracted into its own microservice later with minimal refactor.

**Notable modules:**
- `authentication/` — Registration, login, JWT refresh, RBAC (Patient/Doctor/Admin roles), OTP/2FA.
- `ai_apis/` — A thin gateway layer that forwards requests to the `ai-services/` microservices and normalizes responses back into the platform's API contract (keeps AI infra decoupled from core backend).
- `analytics/` — Aggregation endpoints powering dashboard KPIs (usage, predictions issued, appointment volume, etc.).

---

## 3. AI/ML Services — `ai-services/`

Each AI capability is an **independently trainable, testable, and deployable service** — this is the key to scaling to new AI modules in the future without touching existing ones.

```
ai-services/
├── shared/                            # Common AI infra shared across modules
│   ├── base_model_interface.py        # Abstract class all models implement
│   ├── model_registry.py              # Central model version/lookup registry
│   ├── feature_store/
│   ├── vector_store/                  # FAISS index management
│   ├── monitoring/                    # Model drift & performance monitoring
│   └── utils/
│
├── symptom_checker/
├── disease_prediction/
├── diabetes_prediction/
├── heart_disease_prediction/
├── stroke_prediction/
├── kidney_disease_prediction/
├── medical_report_ocr/
├── medical_report_analyzer/
├── ai_health_chatbot/
├── diet_recommendation/
├── exercise_recommendation/
├── health_risk_score/
├── recommendation_engine/
│
├── model_serving/                     # Unified inference server (FastAPI/TorchServe)
│   ├── app.py
│   ├── routers/
│   └── Dockerfile
│
└── requirements/
    ├── ml.txt                         # scikit-learn, xgboost
    ├── dl.txt                         # tensorflow, torch, transformers
    └── ocr.txt                        # paddleocr, faiss-cpu
```

### 3.1 Standard AI Module Blueprint (applied to all 13 modules above)

```
<ai_module_name>/
├── __init__.py
├── model/                  # Saved model artifacts & architecture definitions
│   ├── architecture.py
│   ├── checkpoints/
│   └── model_config.yaml
├── dataset/                # Raw & processed data (or pointers/DVC refs to storage)
│   ├── raw/
│   ├── processed/
│   └── data_loader.py
├── preprocessing/          # Cleaning, feature engineering, encoding, scaling
│   └── pipeline.py
├── training/                # Training scripts, hyperparameter configs
│   ├── train.py
│   └── config.yaml
├── inference/               # Prediction/serving logic
│   ├── predict.py
│   └── schema.py            # Input/output contracts for this model
├── evaluation/               # Metrics, validation, test-set evaluation
│   ├── evaluate.py
│   └── metrics.py
└── utils/
    └── helpers.py
```

**Purpose:** Isolating `model → dataset → preprocessing → training → inference → evaluation` per module means a data scientist can retrain `heart_disease_prediction` without any risk of breaking `stroke_prediction`. New AI capabilities (e.g., "Cancer Risk Predictor" in the future) are added by copying this exact blueprint into a new sibling folder — zero changes needed elsewhere.

**Module-specific notes:**
- `medical_report_ocr/` — Uses PaddleOCR; inference/ includes text-region detection + text extraction sub-steps.
- `medical_report_analyzer/` — Consumes OCR output; uses Hugging Face NLP models for entity extraction (medications, diagnoses, lab values).
- `ai_health_chatbot/` — Includes an additional `conversation/` folder for dialogue state management and a Hugging Face LLM wrapper.
- `recommendation_engine/` — Uses FAISS for similarity search across patient profiles/content; includes `vector_index/` subfolder.

---

## 4. Flutter Mobile App — `mobile-app/` (Feature-First Architecture)

```
mobile-app/
├── lib/
│   ├── main.dart
│   ├── app.dart                       # MaterialApp/CupertinoApp root widget
│   │
│   ├── core/                          # App-wide foundational code
│   │   ├── constants/
│   │   ├── errors/                    # Failure/exception classes
│   │   ├── network/                   # Dio client, interceptors
│   │   ├── utils/
│   │   └── extensions/
│   │
│   ├── theme/
│   │   ├── app_theme.dart
│   │   ├── colors.dart
│   │   ├── text_styles.dart
│   │   └── dimensions.dart
│   │
│   ├── routing/
│   │   ├── app_router.dart            # go_router / auto_route config
│   │   └── route_names.dart
│   │
│   ├── services/                      # App-level services (not feature-bound)
│   │   ├── api_service.dart
│   │   ├── storage_service.dart       # secure/local storage
│   │   ├── notification_service.dart
│   │   └── analytics_service.dart
│   │
│   ├── models/                        # Shared/global data models
│   │
│   ├── state_management/              # Global state (Riverpod/Bloc/Provider)
│   │   ├── providers/
│   │   └── blocs/
│   │
│   ├── shared_widgets/                # Reusable UI components
│   │   ├── buttons/
│   │   ├── cards/
│   │   ├── inputs/
│   │   └── loaders/
│   │
│   └── features/                      # Feature-first modules
│       ├── authentication/
│       ├── dashboard/
│       ├── home/
│       ├── symptom_checker/
│       ├── disease_prediction/
│       ├── medical_reports/
│       ├── ai_chatbot/
│       ├── profile/
│       ├── settings/
│       └── notifications/
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── test/                              # Unit/widget tests (mirrors lib/)
├── integration_test/
├── pubspec.yaml
└── analysis_options.yaml
```

### 4.1 Standard Feature Blueprint (applied to every folder under `features/`)

```
features/<feature_name>/
├── data/
│   ├── models/            # DTOs / JSON-serializable models
│   ├── datasources/        # Remote (API) & local (cache) data sources
│   └── repositories/       # Repository implementations
├── domain/
│   ├── entities/            # Pure business objects
│   ├── repositories/        # Abstract repository contracts
│   └── usecases/            # Single-responsibility business actions
└── presentation/
    ├── screens/
    ├── widgets/
    └── state/               # Feature-scoped Bloc/Provider/Riverpod state
```

**Purpose:** Follows Flutter Clean Architecture (data/domain/presentation) nested inside Feature-First organization. Each feature is self-contained and independently testable; `shared_widgets/` and `core/` prevent duplication across features without breaking their isolation.

---

## 5. React Web Dashboard — `web-dashboard/`

```
web-dashboard/
├── public/
├── src/
│   ├── index.tsx
│   ├── App.tsx
│   │
│   ├── layouts/
│   │   ├── DoctorLayout/
│   │   ├── AdminLayout/
│   │   └── AuthLayout/
│   │
│   ├── routes/
│   │   ├── AppRoutes.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── roleBasedRoutes.tsx
│   │
│   ├── modules/                       # Feature/domain modules
│   │   ├── doctor-dashboard/
│   │   ├── admin-dashboard/
│   │   ├── analytics/
│   │   ├── patients/
│   │   ├── doctors/
│   │   ├── appointments/
│   │   ├── reports/
│   │   ├── users/
│   │   └── settings/
│   │
│   ├── components/                    # Shared/reusable UI components
│   │   ├── ui/                        # Buttons, inputs, modals, tables
│   │   ├── charts/
│   │   └── common/
│   │
│   ├── hooks/                         # Shared custom hooks
│   │   ├── useAuth.ts
│   │   ├── useFetch.ts
│   │   └── usePagination.ts
│   │
│   ├── api/                           # API layer
│   │   ├── axiosClient.ts
│   │   ├── endpoints.ts
│   │   └── services/                  # One file per backend module
│   │
│   ├── store/                         # Redux Toolkit / Zustand state
│   │   ├── slices/
│   │   └── store.ts
│   │
│   ├── context/                       # React Context providers
│   ├── types/                         # Global TypeScript types/interfaces
│   ├── utils/
│   └── assets/
│
├── tests/
├── .env.example
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 5.1 Standard Module Blueprint (applied to each folder under `modules/`)

```
modules/<module_name>/
├── pages/            # Route-level page components
├── components/        # Module-specific components
├── hooks/             # Module-specific hooks
├── api.ts             # Module-specific API calls
└── types.ts
```

**Purpose:** `doctor-dashboard/` and `admin-dashboard/` act as role-based composition layers pulling widgets from `patients/`, `appointments/`, `analytics/`, etc., avoiding duplication between the two dashboards while keeping role-specific views (e.g., Admin sees user management, Doctor doesn't) cleanly separated via `roleBasedRoutes.tsx`.

---

## 6. Database — `database/`

```
database/
├── postgres/
│   ├── migrations/                    # Alembic-generated or raw SQL migrations
│   ├── seeds/                         # Seed/demo data
│   ├── schema.sql                     # Full reference schema snapshot
│   └── er-diagrams/
├── redis/
│   └── redis.conf
└── backups/
    └── backup_scripts/
```

**Purpose:** Centralizes schema evolution and reference diagrams outside the backend app code so DBAs/architects can review schema changes independent of application logic changes.

---

## 7. Deployment — `deployment/`

```
deployment/
├── docker/
│   ├── backend.Dockerfile
│   ├── ai-services.Dockerfile
│   ├── web-dashboard.Dockerfile
│   └── docker-compose.override.yml
│
├── nginx/
│   ├── nginx.conf
│   ├── conf.d/
│   └── ssl/
│
├── ci-cd/
│   └── github-actions/                # (mirrors .github/workflows for reference/docs)
│       ├── backend-pipeline.yml
│       ├── ai-services-pipeline.yml
│       ├── web-dashboard-pipeline.yml
│       └── mobile-app-pipeline.yml
│
├── terraform/                         # (optional — infra as code)
│   ├── modules/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── main.tf
│
├── kubernetes/                        # (optional — for future orchestration)
│   ├── backend/
│   ├── ai-services/
│   ├── web-dashboard/
│   └── ingress/
│
├── aws/
│   ├── ecs/
│   ├── s3-policies/
│   └── rds/
│
└── environments/
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

**Purpose:** Separates deployment concerns from application code entirely — infra changes (scaling, new environments, cloud migration) don't require touching `backend/` or `ai-services/`. Terraform/Kubernetes are marked optional for teams not yet at that scale, but the folders exist so the structure doesn't need rearchitecting when they're adopted.

---

## 8. Documentation — `docs/`

```
docs/
├── 01-srs/                            # Software Requirements Specification
│   └── srs.md
├── 02-architecture/
│   ├── system-architecture.md
│   ├── backend-architecture.md
│   ├── ai-architecture.md
│   └── diagrams/
├── 03-database-design/
│   ├── er-diagrams/
│   └── data-dictionary.md
├── 04-api-documentation/
│   ├── openapi.yaml
│   └── postman-collection.json
├── 05-ai-pipeline/
│   ├── model-lifecycle.md
│   ├── training-pipeline.md
│   └── model-cards/                   # One card per AI module
├── 06-deployment-guide/
│   ├── local-setup.md
│   ├── staging-deployment.md
│   └── production-deployment.md
├── 07-user-manual/
│   ├── patient-app-guide.md
│   └── doctor-admin-guide.md
└── 08-roadmap/
    └── roadmap.md
```

**Purpose:** Numbered prefixes keep docs in logical reading order for new engineers/stakeholders. `model-cards/` gives each AI module transparent documentation of intended use, training data, and limitations — increasingly expected practice for healthcare AI (relevant for regulatory/compliance review).

---

## 9. Testing — `tests/` (cross-cutting, in addition to per-app test folders)

```
tests/
├── unit/
│   ├── backend/
│   └── ai-services/
├── integration/
│   ├── backend-db/
│   └── backend-ai-services/
├── api/
│   ├── postman/
│   └── pytest-api/
├── ai-model-tests/
│   ├── accuracy-tests/
│   ├── regression-tests/
│   └── bias-fairness-tests/
├── flutter-tests/
│   ├── widget/
│   └── integration/
└── e2e/
    └── playwright/                    # Cross-app end-to-end flows
```

**Purpose:** While unit tests live alongside their respective apps (`backend/tests/`, `mobile-app/test/`), this top-level folder holds tests that span multiple systems — integration, API contract, end-to-end, and AI-specific validations like model accuracy regression and bias/fairness checks, which are critical for healthcare AI compliance.

---

## 10. Supporting Root Folders

```
scripts/
├── setup.sh                           # One-command local environment bootstrap
├── seed_db.sh
├── run_migrations.sh
└── generate_docs.sh

.github/
├── workflows/                         # Actual CI/CD pipelines (backend, AI, web, mobile)
├── ISSUE_TEMPLATE/
└── PULL_REQUEST_TEMPLATE.md
```

---

## 11. Design Principles Applied

| Principle | How it's reflected |
|---|---|
| **Clean Architecture** | Backend modules and Flutter features both separate interface/router → business logic → data access into distinct layers. |
| **Modularity** | Every AI capability, backend domain, and frontend feature is a self-contained folder with an identical internal blueprint. |
| **Scalability for new AI modules** | Adding a new AI capability = copying the standard `model/dataset/preprocessing/training/inference/evaluation/utils` blueprint into a new sibling folder in `ai-services/`. No other folder needs modification. |
| **Separation of concerns** | Frontend (Flutter/React), backend (FastAPI), AI (ai-services), infra (deployment), and data (database) are fully decoupled top-level units, each independently deployable. |
| **Consistency** | Identical sub-structure repeated across all backend modules, all AI modules, all Flutter features, and all React modules — reduces onboarding time and cognitive overhead. |
| **Production readiness** | Dedicated folders for migrations, environment configs, CI/CD, monitoring, model versioning, and compliance-oriented AI documentation (model cards, bias tests). |

---

*This structure is a blueprint only — no source code is included, per project requirements. It's designed so each team (mobile, web, backend, AI/ML, DevOps) can scaffold their respective folder independently using this document as the shared contract.*
