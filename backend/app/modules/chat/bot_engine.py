"""
Rule-based response engine for the AI Health Chatbot.

This is a keyword-matching stand-in for the real RAG pipeline described in the
AI Pipeline doc (FAISS retrieval + LLM generation). It's built this way for the
resume-scope version of this project so the chat module is fully functional and
testable without requiring external LLM API keys or a vector database.

Swapping this out for real RAG later only requires changing `generate_reply()` -
the rest of the module (sessions, message persistence, API contract) doesn't change.
"""

DISCLAIMER = "This is general information, not a medical diagnosis. Please consult a doctor for personalized advice."

_KEYWORD_RESPONSES = {
    "fever": "A fever is often a sign your body is fighting an infection. Stay hydrated and rest. "
             "Seek medical attention if it's above 103°F (39.4°C) or lasts more than 3 days.",
    "headache": "Headaches can result from stress, dehydration, or lack of sleep. Try resting in a "
                "quiet, dark room and drinking water. See a doctor if it's sudden, severe, or recurring.",
    "diabetes": "Diabetes affects how your body processes blood sugar. You can check your risk using "
                "the Diabetes Prediction feature in this app, or discuss symptoms like excessive thirst "
                "or fatigue with your doctor.",
    "chest pain": "Chest pain can have many causes, some serious. If it's severe, sudden, or accompanied "
                  "by shortness of breath, please seek emergency medical care immediately.",
    "appointment": "You can book an appointment with a doctor from the Appointments section of the app.",
    "prescription": "You can view your prescriptions from your doctor in the Prescriptions section of the app.",
    "diet": "A balanced diet with vegetables, whole grains, and lean protein supports overall health. "
            "Check the Recommendations section for a plan personalized to your profile.",
}


def generate_reply(user_message: str) -> str:
    lowered = user_message.lower()

    for keyword, response in _KEYWORD_RESPONSES.items():
        if keyword in lowered:
            return response

    return (
        "I can share general health information, but I'm not able to answer that specific question yet. "
        "For anything concerning, it's best to consult with a doctor through the Appointments section."
    )
