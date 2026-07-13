# MedAssist AI — System Architecture

## 1. High-Level Architecture

```mermaid
flowchart TB
    subgraph Clients
        MOB[Flutter Mobile App - Patient]
        WEB[React Web Dashboard - Doctor/Admin]
    end

    subgraph EdgeLayer["Edge / Gateway"]
        LB[Load Balancer / Nginx]
        WAF[WAF + Rate Limiter]
    end

    subgraph AppLayer["Application Layer"]
        API[FastAPI Backend]
        AIGW[AI Gateway - ai_apis module]
    end

    subgraph AILayer["AI/ML Microservices"]
        SC[Symptom Checker]
        DP[Disease Prediction x4]
        OCR[Medical Report OCR]
        RA[Report Analyzer]
        CB[AI Chatbot - RAG]
        REC[Recommendation Engine]
        HRS[Health Risk Score]
    end

    subgraph DataLayer["Data Layer"]
        PG[(PostgreSQL)]
        REDIS[(Redis)]
        FAISSDB[(FAISS Vector Store)]
        S3[(Object Storage - Reports)]
    end

    subgraph Infra["Infrastructure"]
        DOCKER[Docker / Docker Compose]
        CICD[GitHub Actions CI/CD]
        MON[Monitoring & Logging]
    end

    MOB --> LB
    WEB --> LB
    LB --> WAF --> API
    API --> AIGW
    AIGW --> SC & DP & OCR & RA & CB & REC & HRS
    API --> PG
    API --> REDIS
    API --> S3
    CB --> FAISSDB
    REC --> FAISSDB
    API --> MON
    AILayer --> MON
```

**Rationale:** The AI Gateway (`ai_apis` backend module) acts as an anti-corruption layer between the core backend and the AI microservices — the backend never calls AI models directly, so AI services can be scaled, versioned, or replaced without touching backend business logic. This also centralizes AI request logging, rate limiting, and response normalization in one place.

---

## 2. Component Diagram

```mermaid
flowchart LR
    subgraph Backend["FastAPI Backend"]
        AUTH[Authentication]
        USR[Users]
        PAT[Patients]
        DOC[Doctors]
        APT[Appointments]
        MR[Medical Reports]
        PRE[Prescriptions]
        NOT[Notifications]
        CHT[Chat]
        AIA[AI APIs Gateway]
        ANA[Analytics]
        FU[File Upload]
        SET[Settings]
    end

    AUTH --> USR
    USR --> PAT
    USR --> DOC
    PAT --> APT
    DOC --> APT
    PAT --> MR
    MR --> FU
    DOC --> PRE
    PAT --> CHT
    CHT --> AIA
    MR --> AIA
    PAT --> AIA
    ANA --> USR
    ANA --> AIA
    NOT --> PAT
    NOT --> DOC
```

Each block corresponds directly to a backend module (`app/modules/<name>`) following the router → service → repository → model layering defined in the Folder Structure document.

---

## 3. Deployment Diagram

```mermaid
flowchart TB
    subgraph CloudRegion["AWS Region (Primary)"]
        subgraph PublicSubnet["Public Subnet"]
            ALB[Application Load Balancer]
            NGX[Nginx Reverse Proxy]
        end

        subgraph PrivateSubnet["Private Subnet - Compute"]
            subgraph ECS["ECS / Docker Cluster"]
                BE1[Backend Container x N]
                AI1[AI Service Containers x N]
                WORKER[Async Worker - OCR/Notification Jobs]
            end
        end

        subgraph DataSubnet["Private Subnet - Data"]
            RDS[(RDS PostgreSQL - Multi-AZ)]
            ELASTICACHE[(ElastiCache Redis)]
            VECTORSTORE[(FAISS Index - EFS/EBS backed)]
        end

        S3B[(S3 - Medical Reports/Assets)]
        CW[CloudWatch - Logs & Metrics]
    end

    CDN[CloudFront CDN] --> WEBAPP[React Static Build]
    ALB --> NGX --> BE1
    BE1 --> AI1
    BE1 --> RDS
    BE1 --> ELASTICACHE
    BE1 --> S3B
    AI1 --> VECTORSTORE
    WORKER --> RDS
    WORKER --> S3B
    BE1 --> CW
    AI1 --> CW
```

**Notes:**
- Backend and AI services run as separate container groups so each can be scaled independently based on load (AI inference is typically more CPU/GPU-intensive than CRUD API traffic).
- `WORKER` handles asynchronous, longer-running jobs (OCR processing, notification dispatch) via a Redis-backed queue (Celery/RQ), keeping the main API responsive.
- Multi-AZ RDS for PostgreSQL provides high availability; Redis via managed ElastiCache for session/cache reliability.

---

## 4. Microservice Boundaries

| Service | Responsibility | Scaling driver |
|---|---|---|
| Core Backend (FastAPI) | Auth, CRUD, orchestration, business rules | Request volume (CPU) |
| AI Gateway | Routes/normalizes calls to AI services, applies AI-specific rate limits | Request volume |
| Symptom Checker Service | NLP inference | Inference load (CPU/GPU) |
| Disease Prediction Services (x4) | Tabular ML inference | Inference load (CPU) |
| OCR Service | Document processing | Job queue depth (CPU/GPU, batch-friendly) |
| Report Analyzer Service | Rule engine + LLM summarization | Inference load (CPU/GPU) |
| Chatbot Service | RAG retrieval + LLM generation | Concurrent sessions (CPU/GPU + memory for vector index) |
| Recommendation Engine | Rule + similarity search | Low — lightweight, CPU only |
| Health Risk Score Service | Aggregation of other model outputs | Low — depends on upstream services |
| Async Worker | OCR jobs, notifications | Queue depth |

Each AI service is independently containerized (own Dockerfile, own `requirements`) which directly maps to the `ai-services/<module>/` folder structure — enabling independent deployment pipelines per module (see CI/CD in Deployment Guide).

---

## 5. Communication & Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant Nginx
    participant Backend
    participant Redis
    participant AIGateway
    participant AIService
    participant Postgres

    Client->>Nginx: HTTPS Request
    Nginx->>Backend: Forward (internal network)
    Backend->>Redis: Check rate limit / cache
    alt Cache hit
        Redis-->>Backend: Cached response
    else Cache miss
        Backend->>Postgres: Query/Write
        alt Requires AI inference
            Backend->>AIGateway: Forward request
            AIGateway->>AIService: gRPC/HTTP call
            AIService-->>AIGateway: Prediction result
            AIGateway-->>Backend: Normalized response
            Backend->>Postgres: Persist prediction
        end
    end
    Backend-->>Client: JSON Response
```

- **Synchronous** communication (HTTP/REST or gRPC) is used between Backend ↔ AI Gateway ↔ AI Services for real-time predictions (symptom checker, disease prediction, chatbot).
- **Asynchronous** communication (Redis-backed queue) is used for OCR processing and notification dispatch, since these are not required to complete within the request/response cycle.

---

## 6. Why Microservices for AI, Modular Monolith for Backend

- The **core backend** is deployed as a modular monolith (single FastAPI app, internally organized into clean modules) rather than full microservices — at MedAssist AI's expected scale, this reduces operational overhead (one deployment, one DB connection pool to manage) while the clean module boundaries (`router/service/repository`) keep the code ready to be split into true microservices later if a specific module's load justifies it.
- The **AI layer** is microservices from day one because: (a) AI workloads have fundamentally different resource profiles (GPU vs CPU, batch vs real-time) than CRUD workloads, (b) AI models are retrained/redeployed on independent cadences, and (c) isolating AI services limits the blast radius if a specific model misbehaves or needs rollback.
