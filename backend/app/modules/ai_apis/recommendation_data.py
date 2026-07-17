"""
Curated diet/exercise plan library for the Recommendation Engine.

Per the AI Pipeline doc, this module is deliberately RULE-BASED rather than a
trained model: "a hybrid rule + retrieval system guarantees clinically-vetted
safety constraints are always respected... avoids the risk of a purely
generative recommender suggesting something contraindicated for a patient's
condition." The full design also describes a FAISS similarity layer for
personalization variety - omitted here to keep this resume-scope module
dependency-light; the rule-based safety-filtering layer (the part that
actually matters for correctness) is what's implemented.

Every plan is clinician-guideline-inspired (general dietary/exercise advice
commonly given for these conditions) but this is NOT a substitute for
individualized medical advice - the API response always includes a disclaimer.
"""

DIET_PLANS = {
    "renal_friendly": {
        "title": "Kidney-Friendly Low-Sodium, Low-Potassium Plan",
        "items": [
            "Limit sodium to under 2,000mg/day - avoid processed and canned foods",
            "Choose lower-potassium fruits (apples, berries, grapes) over bananas/oranges",
            "Moderate protein portions - consult your doctor for a target gram amount",
            "Limit phosphorus-heavy foods (dairy, nuts, cola drinks)",
            "Stay within your doctor-recommended fluid intake",
        ],
    },
    "diabetic_friendly": {
        "title": "Low-Glycemic, Blood-Sugar-Friendly Plan",
        "items": [
            "Favor whole grains over refined carbs (brown rice, whole wheat, oats)",
            "Pair carbohydrates with protein or fiber to slow glucose absorption",
            "Limit added sugars and sugary beverages",
            "Eat at consistent times to help stabilize blood sugar",
            "Include non-starchy vegetables at most meals",
        ],
    },
    "heart_healthy": {
        "title": "Heart-Healthy, Low-Sodium Plan",
        "items": [
            "Limit sodium to under 1,500-2,000mg/day",
            "Favor unsaturated fats (olive oil, nuts, fish) over saturated/trans fats",
            "Increase soluble fiber (oats, beans, fruits) to help manage cholesterol",
            "Limit red and processed meats",
            "Include fatty fish (salmon, mackerel) 2x/week if not contraindicated",
        ],
    },
    "weight_loss": {
        "title": "Calorie-Conscious Weight Management Plan",
        "items": [
            "Aim for a moderate calorie deficit (consult a dietitian for your target)",
            "Prioritize protein and fiber for satiety",
            "Reduce portion sizes of calorie-dense, low-nutrient foods",
            "Stay hydrated - thirst is often mistaken for hunger",
            "Plan meals ahead to avoid impulsive high-calorie choices",
        ],
    },
    "weight_gain": {
        "title": "Healthy Weight Gain Plan",
        "items": [
            "Add calorie-dense, nutrient-rich foods (nuts, avocado, whole milk)",
            "Eat more frequently - 5-6 smaller meals rather than 3 large ones",
            "Include a protein source at every meal to support muscle gain",
            "Pair strength training with your increased intake",
        ],
    },
    "balanced_maintenance": {
        "title": "Balanced Maintenance Plan",
        "items": [
            "Follow a varied diet with plenty of vegetables, whole grains, and lean protein",
            "Practice portion awareness rather than strict restriction",
            "Stay hydrated throughout the day",
            "Limit ultra-processed foods where practical",
        ],
    },
}

EXERCISE_PLANS = {
    "low_impact_cardiac_safe": {
        "title": "Low-Impact, Cardiac-Safe Movement Plan",
        "items": [
            "Start with 10-15 minutes of walking daily, progressing gradually",
            "Avoid high-intensity or heavy-lifting exercise without medical clearance",
            "Include gentle stretching or chair yoga",
            "Monitor for chest pain, dizziness, or breathlessness and stop if they occur",
            "Always warm up and cool down gradually",
        ],
    },
    "gentle_mobility": {
        "title": "Gentle Mobility & Balance Plan",
        "items": [
            "Daily short walks (10-20 minutes) at a comfortable pace",
            "Balance exercises (e.g. standing on one foot near a support) to reduce fall risk",
            "Gentle range-of-motion stretching",
            "Avoid sudden, jarring movements",
        ],
    },
    "weight_loss_cardio": {
        "title": "Cardio-Focused Weight Loss Plan",
        "items": [
            "150+ minutes/week of moderate cardio (brisk walking, cycling, swimming)",
            "Add 2 days/week of light strength training to preserve muscle mass",
            "Gradually increase duration/intensity as fitness improves",
            "Track activity to stay consistent",
        ],
    },
    "strength_building": {
        "title": "Strength & Muscle-Building Plan",
        "items": [
            "Resistance training 3-4 days/week, covering all major muscle groups",
            "Progressive overload - gradually increase weight/reps over time",
            "Ensure adequate rest days between sessions for the same muscle group",
            "Pair with adequate protein intake",
        ],
    },
    "general_fitness": {
        "title": "General Fitness Plan",
        "items": [
            "150 minutes/week of moderate-intensity activity (walking, cycling, swimming)",
            "2 days/week of strength training",
            "Include flexibility/mobility work",
            "Choose activities you enjoy to support consistency",
        ],
    },
}
