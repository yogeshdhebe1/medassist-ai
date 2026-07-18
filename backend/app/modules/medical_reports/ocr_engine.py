import os
import re

import pytesseract
from PIL import Image

from app.config import settings
from app.modules.medical_reports.reference_ranges import REFERENCE_RANGES

# On Windows, Tesseract isn't automatically on PATH after installation the way
# it is on Linux (apt) - point pytesseract at the configured path (read via the
# app's Settings object, which loads .env through pydantic-settings - reading
# os.environ directly here would NOT pick up .env values, since pydantic-settings
# populates the Settings object without necessarily mirroring into os.environ).
if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def extract_text(file_path: str) -> str:
    """Runs Tesseract OCR on an image file and returns the raw extracted text."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Report file not found at {file_path}")

    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


def extract_structured_values(raw_text: str) -> dict:
    """Parses raw OCR text for known lab test names and their numeric values.

    This is intentionally a known-vocabulary regex matcher (matching against
    REFERENCE_RANGES' test names) rather than a general-purpose table/layout
    parser - a real production OCR pipeline would need more robust table
    structure recognition (which is part of why PaddleOCR, with its table
    recognition models, is the production choice per the AI Pipeline doc).
    """
    extracted = {}
    confidence_notes = []

    lowered = raw_text.lower()
    lines = lowered.split("\n")

    for test_key, range_info in REFERENCE_RANGES.items():
        pattern = re.escape(test_key).replace(r"\ ", r"\s+") + r".*?([\d,]+\.?\d*)"
        found = False
        for line in lines:
            match = re.search(pattern, line)
            if match:
                value_str = match.group(1).replace(",", "")
                try:
                    value = float(value_str)
                    extracted[test_key] = {
                        "value": value,
                        "unit": range_info["unit"],
                        "display_name": range_info["display_name"],
                    }
                    found = True
                except ValueError:
                    pass
                break
        if not found:
            confidence_notes.append(test_key)

    total_known = len(REFERENCE_RANGES)
    confidence = round(len(extracted) / total_known, 4) if total_known else 0.0

    return {
        "extracted_fields": extracted,
        "confidence_score": confidence,
        "raw_text": raw_text,
    }
