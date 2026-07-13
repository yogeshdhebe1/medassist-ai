# MedAssist AI — Documentation Set

**AI-Powered Intelligent Healthcare Platform**

This documentation set is intended to be handed to a development team as the architectural and planning foundation for building MedAssist AI. It contains no application code — planning and architecture only.

## Contents

| # | Document | Description |
|---|---|---|
| 01 | [Software Requirements Specification](./01-Software-Requirements-Specification.md) | Problem statement, objectives, scope, functional & non-functional requirements, success metrics |
| 02 | [User Flows](./02-User-Flows.md) | Patient, Doctor, and Admin flows with Mermaid diagrams |
| 03 | [Database Design](./03-Database-Design.md) | ER diagram, table definitions, data dictionary, indexing strategy |
| 04 | [API Design](./04-API-Design.md) | Full REST API specification across all domains |
| 05 | [AI Pipeline](./05-AI-Pipeline.md) | Dataset → training → deployment lifecycle for every AI module |
| 06 | [System Architecture](./06-System-Architecture.md) | High-level, component, deployment, and data-flow diagrams |
| 07 | [Security Architecture](./07-Security-Architecture.md) | Auth, RBAC, encryption, audit logging, PHI-specific controls |
| 08 | [Folder Structure](./08-Folder-Structure.md) | Enterprise monorepo layout for all subsystems |
| 09 | [Development Roadmap](./09-Development-Roadmap.md) | 24-week, phase-by-phase, sprint-level delivery plan |
| 10 | [Future Enhancements](./10-Future-Enhancements.md) | Post-v1 scope: wearables, voice, telemedicine, integrations |

## System Snapshot

- **Users:** Patient, Doctor, Admin (future: Hospital, Laboratory, Insurance)
- **Clients:** Flutter (patient mobile app), React (doctor/admin web dashboard)
- **Backend:** FastAPI (Python), modular monolith with clean architecture layering
- **AI/ML:** 7 independent AI modules (Symptom Checker, 4x Disease Prediction, OCR, Report Analyzer, Chatbot, Recommendation Engine, Health Risk Score) served as independent microservices
- **Data:** PostgreSQL (primary), Redis (cache/session/queue), FAISS (vector search)
- **Deployment:** Docker, Docker Compose, GitHub Actions CI/CD, AWS

## How to Use This Documentation

1. Start with the **SRS** to align on scope and requirements.
2. Review **User Flows** and **System Architecture** together to understand how requirements map to system behavior.
3. Use **Database Design** and **API Design** as the implementation contract for backend engineers.
4. Use **AI Pipeline** as the implementation contract for ML engineers, module by module.
5. Use **Folder Structure** to scaffold the repository before writing any code.
6. Use **Security Architecture** as a mandatory checklist before any PHI-handling feature ships.
7. Use the **Development Roadmap** for sprint planning; revisit **Future Enhancements** once v1 is stable.

> ⚠️ MedAssist AI's outputs are clinical decision-support and patient-engagement tools only. They are advisory and do not constitute medical diagnosis. This must be reflected clearly in all UI touchpoints across the mobile and web clients.
