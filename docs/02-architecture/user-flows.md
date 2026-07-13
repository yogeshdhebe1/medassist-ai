# MedAssist AI — User Flows

Flows are represented as Mermaid diagrams for direct rendering in GitHub/GitLab markdown.

---

## 1. Patient User Flow

### 1.1 Onboarding & Authentication

```mermaid
flowchart TD
    A[App Launch] --> B{Existing Account?}
    B -- No --> C[Register: Email/Phone]
    C --> D[Verify OTP]
    D --> E[Complete Profile: Age, Gender, History]
    E --> F[Patient Dashboard]
    B -- Yes --> G[Login: Email/Password or OTP]
    G --> H{Valid Credentials?}
    H -- No --> G
    H -- Yes --> F
```

### 1.2 Core Patient Journey

```mermaid
flowchart TD
    F[Patient Dashboard] --> S1[Symptom Checker]
    F --> S2[Upload Medical Report]
    F --> S3[Disease Prediction]
    F --> S4[AI Health Chatbot]
    F --> S5[Recommendations]
    F --> S6[Medicine Reminders]

    S1 --> R1[Enter/Select Symptoms]
    R1 --> R2[AI Inference: Possible Diseases]
    R2 --> R3[View Ranked Results + Confidence]
    R3 --> R4{Escalate to Doctor?}
    R4 -- Yes --> R5[Book/Message Doctor]
    R4 -- No --> F

    S2 --> U1[Select File: PDF/Image]
    U1 --> U2[OCR Extraction]
    U2 --> U3[AI Report Analyzer: Abnormal Values + Summary]
    U3 --> U4[View Explained Report]
    U4 --> F

    S3 --> P1[Enter Clinical Inputs]
    P1 --> P2[AI Prediction: Diabetes/Heart/Stroke/Kidney]
    P2 --> P3[View Risk Score + Explanation]
    P3 --> F

    S4 --> C1[Ask Question]
    C1 --> C2[RAG Retrieval from Knowledge Base + Patient Context]
    C2 --> C3[LLM Generates Answer]
    C3 --> C4[Disclaimer + Optional Doctor Escalation]
    C4 --> F

    S5 --> D1[View Diet Plan]
    S5 --> D2[View Exercise Plan]
    D1 --> F
    D2 --> F

    S6 --> M1[Set Reminder Schedule]
    M1 --> M2[Receive Push Notification]
    M2 --> F
```

---

## 2. Doctor User Flow

```mermaid
flowchart TD
    A[Doctor Login] --> B[Doctor Dashboard]
    B --> C[Patient List]
    C --> D[Select Patient]
    D --> E[View Patient Profile & History]
    E --> F[View Uploaded Reports + AI Summaries]
    E --> G[View AI Risk Scores & Predictions]
    E --> H[Create/Update Prescription]
    H --> I[Save Prescription]
    I --> J[Patient Notified]
    E --> K[Add Clinical Notes]
    K --> L[Timeline Updated]
```

---

## 3. Admin User Flow

```mermaid
flowchart TD
    A[Admin Login] --> B[Admin Dashboard]
    B --> C[User Management]
    B --> D[Doctor Management]
    B --> E[Analytics Dashboard]
    B --> F[AI Monitoring]
    B --> G[Reports & Exports]

    C --> C1[View/Suspend/Delete Patient Accounts]
    D --> D1[Approve/Onboard Doctor]
    D --> D2[Suspend/Remove Doctor]
    E --> E1[Usage Metrics]
    E --> E2[Prediction Volume]
    F --> F1[Model Latency/Error Rate]
    F --> F2[Drift Alerts]
    G --> G1[Export CSV/PDF Reports]
```

---

## 4. Cross-Cutting Flow: Medical Report Lifecycle

```mermaid
sequenceDiagram
    participant P as Patient (Flutter App)
    participant BE as FastAPI Backend
    participant OCR as OCR Service (PaddleOCR)
    participant NLP as Report Analyzer (NLP)
    participant DB as PostgreSQL

    P->>BE: Upload report (PDF/Image)
    BE->>DB: Store file metadata + reference
    BE->>OCR: Send file for text/value extraction
    OCR-->>BE: Structured extracted values
    BE->>NLP: Send extracted values for analysis
    NLP-->>BE: Abnormal values, summary, next-step suggestions
    BE->>DB: Persist analysis result
    BE-->>P: Return report summary + flagged values
```

---

## 5. Cross-Cutting Flow: AI Chatbot (RAG)

```mermaid
sequenceDiagram
    participant P as Patient
    participant BE as Backend (AI Gateway)
    participant VDB as Vector DB (FAISS)
    participant LLM as LLM Service

    P->>BE: Ask question
    BE->>VDB: Retrieve relevant medical knowledge + patient context
    VDB-->>BE: Top-k relevant chunks
    BE->>LLM: Prompt = question + retrieved context
    LLM-->>BE: Generated answer
    BE-->>P: Answer + citations + medical disclaimer
```
