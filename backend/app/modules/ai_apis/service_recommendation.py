import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.modules.ai_apis.models import AIPrediction
from app.modules.ai_apis.recommendation_data import DIET_PLANS, EXERCISE_PLANS
from app.modules.patients.repository import PatientRepository


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)

    def _get_latest_risk_level(self, patient_id: uuid.UUID, prediction_type: str) -> str | None:
        latest = (
            self.db.query(AIPrediction)
            .filter(AIPrediction.patient_id == patient_id, AIPrediction.prediction_type == prediction_type)
            .order_by(AIPrediction.created_at.desc())
            .first()
        )
        if latest and isinstance(latest.output_result, dict):
            return latest.output_result.get("risk_level")
        return None

    def _get_patient_context(self, user_id: uuid.UUID) -> dict:
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            patient = self.patient_repo.create(user_id)

        age = None
        if patient.date_of_birth:
            today = date.today()
            age = today.year - patient.date_of_birth.year - (
                (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
            )

        bmi = None
        if patient.height_cm and patient.weight_kg:
            height_m = patient.height_cm / 100
            bmi = round(patient.weight_kg / (height_m**2), 1)

        return {
            "patient_id": patient.id,
            "age": age,
            "bmi": bmi,
            "diabetes_risk": self._get_latest_risk_level(patient.id, "diabetes"),
            "heart_risk": self._get_latest_risk_level(patient.id, "heart_disease"),
            "kidney_risk": self._get_latest_risk_level(patient.id, "kidney_disease"),
            "stroke_risk": self._get_latest_risk_level(patient.id, "stroke"),
        }

    def _infer_goal(self, ctx: dict, goal_override: str | None) -> str:
        if goal_override:
            return goal_override
        if ctx["bmi"] is not None:
            if ctx["bmi"] >= 30:
                return "weight_loss"
            if ctx["bmi"] < 18.5:
                return "muscle_gain"  # mapped to weight_gain diet / strength-building exercise
        return "maintenance"

    def get_diet_recommendation(self, user_id: uuid.UUID, goal_override: str | None) -> dict:
        ctx = self._get_patient_context(user_id)
        goal = self._infer_goal(ctx, goal_override)

        reasons = []
        # Safety-first ordering: clinical contraindications take priority over goal-based selection.
        if ctx["kidney_risk"] in ("medium", "high"):
            plan_key = "renal_friendly"
            reasons.append(f"kidney disease risk is '{ctx['kidney_risk']}'")
        elif ctx["diabetes_risk"] in ("medium", "high"):
            plan_key = "diabetic_friendly"
            reasons.append(f"diabetes risk is '{ctx['diabetes_risk']}'")
        elif ctx["heart_risk"] in ("medium", "high") or ctx["stroke_risk"] in ("medium", "high"):
            plan_key = "heart_healthy"
            reasons.append("elevated cardiovascular/stroke risk")
        elif goal == "weight_loss":
            plan_key = "weight_loss"
            reasons.append(f"BMI of {ctx['bmi']} suggests a weight-management focus" if ctx["bmi"] else "weight-loss goal selected")
        elif goal == "muscle_gain":
            plan_key = "weight_gain"
            reasons.append(f"BMI of {ctx['bmi']} suggests a weight-gain focus" if ctx["bmi"] else "weight-gain goal selected")
        else:
            plan_key = "balanced_maintenance"
            reasons.append("no elevated disease risk detected; general maintenance guidance")

        plan = DIET_PLANS[plan_key]
        rationale = f"Selected based on: {'; '.join(reasons)}."
        return {"title": plan["title"], "plan": plan["items"], "rationale": rationale}

    def get_exercise_recommendation(self, user_id: uuid.UUID, goal_override: str | None) -> dict:
        ctx = self._get_patient_context(user_id)
        goal = self._infer_goal(ctx, goal_override)

        reasons = []
        if ctx["heart_risk"] in ("medium", "high") or ctx["stroke_risk"] in ("medium", "high"):
            plan_key = "low_impact_cardiac_safe"
            reasons.append("elevated cardiovascular/stroke risk - high-intensity exercise avoided for safety")
        elif ctx["age"] is not None and ctx["age"] >= 65:
            plan_key = "gentle_mobility"
            reasons.append(f"age {ctx['age']} - prioritizing mobility and fall-prevention")
        elif goal == "weight_loss":
            plan_key = "weight_loss_cardio"
            reasons.append("weight-loss goal - cardio-focused plan")
        elif goal == "muscle_gain":
            plan_key = "strength_building"
            reasons.append("muscle-gain goal - strength-focused plan")
        else:
            plan_key = "general_fitness"
            reasons.append("no elevated risk detected; general fitness guidance")

        plan = EXERCISE_PLANS[plan_key]
        rationale = f"Selected based on: {'; '.join(reasons)}."
        return {"title": plan["title"], "plan": plan["items"], "rationale": rationale}
