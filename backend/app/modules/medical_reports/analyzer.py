"""
Rule-based medical report analyzer - flags abnormal values against reference
ranges and generates a plain-language summary.

SCOPING NOTE: the AI Pipeline doc describes this module as a deterministic
rule engine (for the clinically-critical "is this abnormal" decision) PLUS an
LLM for natural-language explanation, explicitly designed so "no LLM output
should contradict deterministic thresholds." This implementation keeps the
deterministic rule engine (the part that matters for correctness) and
generates the plain-language summary via **string templates** rather than a
real LLM call - the same honest-scoping pattern as the chatbot and symptom
checker. The rule-engine output (`abnormal_values`) is the single source of
truth; the "summary" text is just a readable rendering of it, so there's no
risk of the two disagreeing (which is the actual property the AI Pipeline doc
cared about - the LLM/no-LLM distinction is secondary to that guarantee).
"""

from app.modules.medical_reports.reference_ranges import REFERENCE_RANGES


def analyze_extracted_values(extracted_fields: dict) -> dict:
    abnormal_values = []
    normal_values = []

    for test_key, field in extracted_fields.items():
        range_info = REFERENCE_RANGES.get(test_key)
        if not range_info:
            continue

        value = field["value"]
        is_low = value < range_info["low"]
        is_high = value > range_info["high"]

        entry = {
            "test": field["display_name"],
            "value": value,
            "unit": field["unit"],
            "reference_range": f"{range_info['low']}-{range_info['high']} {field['unit']}",
        }

        if is_low:
            entry["flag"] = "low"
            abnormal_values.append(entry)
        elif is_high:
            entry["flag"] = "high"
            abnormal_values.append(entry)
        else:
            normal_values.append(entry)

    summary = _generate_summary(abnormal_values, normal_values)
    next_steps = _generate_next_steps(abnormal_values)

    return {
        "abnormal_values": abnormal_values,
        "normal_values": normal_values,
        "summary": summary,
        "next_steps": next_steps,
    }


def _generate_summary(abnormal_values: list, normal_values: list) -> str:
    if not abnormal_values:
        return (
            f"All {len(normal_values)} extracted test value(s) fall within the typical "
            f"reference range for this report."
        )

    parts = []
    for entry in abnormal_values:
        direction = "higher than" if entry["flag"] == "high" else "lower than"
        parts.append(
            f"{entry['test']} is {entry['value']} {entry['unit']}, {direction} the typical "
            f"range ({entry['reference_range']})"
        )

    summary = f"{len(abnormal_values)} of {len(abnormal_values) + len(normal_values)} extracted values are outside the typical range: "
    summary += "; ".join(parts) + "."
    return summary


def _generate_next_steps(abnormal_values: list) -> str:
    if not abnormal_values:
        return "No abnormal values detected in this report. Continue routine follow-up as advised by your doctor."

    flagged_tests = ", ".join(e["test"] for e in abnormal_values)
    return (
        f"Discuss the following results with your doctor at your next visit or sooner if "
        f"you have symptoms: {flagged_tests}. This automated analysis is not a diagnosis - "
        f"only a licensed clinician can interpret these results in the context of your full "
        f"medical history."
    )
