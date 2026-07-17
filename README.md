# Recommendation Engine — Update Package

Adds diet and exercise recommendations — the last AI module from the SRS's original 7-module list (Symptom Checker, 4x Disease Prediction, Chatbot, and this one are now all done; Medical Report OCR/Analyzer remain, covered separately since they need actual image files to test meaningfully).

## Design: rule-based, not a trained model — and why

Per the AI Pipeline doc: *"A hybrid rule + retrieval system guarantees clinically-vetted safety constraints are always respected... avoids the risk of a purely generative recommender suggesting something contraindicated for a patient's condition."* This module implements the rule-based safety-filtering half of that design (the part that actually matters for correctness); the FAISS similarity-based personalization-variety layer is omitted to keep this dependency-light for a resume-scope project.

**Safety-first selection order**: clinical contraindications always override goal-based preferences. If a patient has elevated kidney disease risk, they get the renal-friendly diet **regardless of their weight-loss goal** — a purely goal-driven recommender could suggest something clinically inappropriate, which is exactly the failure mode this design avoids.

## How it decides what to recommend

1. **Fetches the patient's context**: age (from date of birth), BMI (from height/weight), and their **most recent** risk_level from each of the 4 disease-prediction models (reuses your existing `ai_predictions` data — no new questions asked of the patient).
2. **Diet selection priority**: kidney risk → heart/stroke risk → diabetes risk → goal-based (weight loss/gain) → general maintenance.
3. **Exercise selection priority**: heart/stroke risk (low-impact only) → age ≥65 (mobility-focused) → goal-based → general fitness.
4. Every response includes a **rationale** explaining which factor drove the selection, and a **disclaimer** that this is general guidance, not individualized medical advice.

## What's included

- `app/modules/ai_apis/recommendation_data.py` — **new file**: the curated diet/exercise plan library (11 plans total)
- `app/modules/ai_apis/schemas_recommendation.py` — **new file**
- `app/modules/ai_apis/service_recommendation.py` — **new file**: the selection logic
- `app/modules/ai_apis/router.py` — **overwrite**: adds the 2 new endpoints (built on the version from the Symptom Checker update — includes everything from before too)

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/ai/recommendations/diet` | Bearer (role: patient) | Get a diet plan (optional `{"goal": "weight_loss"\|"maintenance"\|"muscle_gain"}` override) |
| POST | `/v1/ai/recommendations/exercise` | Bearer (role: patient) | Get an exercise plan (same optional override) |

## How to apply

1. Add the 3 new files to `backend/app/modules/ai_apis/`.
2. Overwrite `backend/app/modules/ai_apis/router.py`.
3. **No new dependencies, no migration needed** — reuses existing patient profile + `ai_predictions` data.
4. Restart: `uvicorn app.main:app --reload`

## How to test in Swagger UI

Since this reads your patient's profile and prediction history, results will vary based on what you've already tested. A few scenarios to try:

1. **Baseline**: `POST /v1/ai/recommendations/diet` with an empty body `{}` → since your test patient's profile has `height_cm: 175, weight_kg: 70` (BMI ~22.9, normal) and has run a heart disease prediction with `"risk_level": "high"` earlier in this session, expect the **heart-healthy plan**, with rationale mentioning "elevated cardiovascular/stroke risk."
2. `POST /v1/ai/recommendations/exercise` with `{}` → expect the **low-impact cardiac-safe plan**, same reasoning.
3. **Goal override test**: `POST /v1/ai/recommendations/diet` with `{"goal": "weight_loss"}` → the response should **still** return the heart-healthy plan, not the weight-loss plan — this proves the safety-first priority ordering works (clinical risk beats stated goal).
4. To see the goal-based path instead, you'd need a patient with no elevated disease risk history.

## Design notes

- **Read-only, no new questions asked**: unlike the disease-prediction endpoints, this doesn't take clinical inputs directly — it reuses data the patient has already provided (profile + past predictions), which is a deliberately different interaction pattern worth mentioning if asked to compare the modules.
- **Static plan library vs. FAISS retrieval**: the AI Pipeline doc's "curated plan library + nearest-neighbor retrieval" becomes, in this scope, a small fixed set of clinician-guideline-inspired plans selected by explicit rules. This trades personalization variety (FAISS would surface different plan *variants* for similar patients) for simplicity and zero extra infrastructure — an honest scope reduction to mention if asked about the gap between this and the full design.
