# Medical Report OCR + Analyzer — Update Package

Adds the **last AI module** from the SRS's original list — extracts structured lab values from an uploaded report image (OCR) and flags abnormal values against reference ranges (rule-based analysis).

## ⚠️ Two setup steps unique to this module (read before applying)

### 1. Install Tesseract OCR (a system program, not just a Python package)

Unlike every previous module, this one needs a **non-Python program** installed on your machine — `pytesseract` is just a thin Python wrapper around the actual Tesseract OCR engine.

**Windows:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki (the UB-Mannheim build is the standard Windows distribution)
2. Run it, noting the install path (default is usually `C:\Program Files\Tesseract-OCR\`)
3. Add this to your `.env` file:
   ```
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```
   (This backend code reads this env var and points `pytesseract` at it — without it, Windows won't find Tesseract since it's not automatically added to PATH the way it is on Linux.)

### 2. Why Tesseract instead of PaddleOCR (honest scoping note)

The AI Pipeline doc specifies **PaddleOCR** for this module — chosen there for strong multilingual and table-structure recognition suitable for production. PaddleOCR requires the PaddlePaddle deep-learning framework plus multi-GB model downloads, which isn't practical for a resume-scope local project.

**Tesseract OCR** is used instead — a single lightweight system package, much faster to install, and it demonstrates the identical architectural pattern (image → OCR text → structured parsing → rule-based analysis). The tradeoff: Tesseract does plain text extraction without PaddleOCR's table-structure awareness, so this implementation uses a **known-vocabulary regex parser** (matching against a fixed list of common lab test names) rather than general table-layout understanding. **This is a good, honest talking point for an interview** — explaining you understand the production-vs-resume-scope tradeoff, and specifically *what* capability was traded away (table structure recognition) for practicality.

## What it does

1. **OCR** (`ocr_engine.py`): runs Tesseract on an uploaded report image, then a regex parser extracts recognized lab test values (currently recognizes 12 common tests: Hemoglobin, Glucose, WBC Count, Platelet Count, Creatinine, Total Cholesterol, Blood Urea, Sodium, Potassium, RBC Count, HbA1c, Triglycerides).
2. **Analysis** (`analyzer.py`): compares each extracted value against a reference range table, flags abnormal ones (high/low), and generates a plain-language summary + suggested next steps.

## Test asset included

`test-assets/sample_lab_report.png` — a synthetic lab report I generated (not a real scanned document, since none was available) with **known abnormal values built in**, so you can verify the whole pipeline works correctly:

| Test | Value | Reference Range | Expected flag |
|---|---|---|---|
| Hemoglobin | 9.8 g/dL | 13.0-17.0 | **low** |
| Glucose (Fasting) | 145 mg/dL | 70-100 | **high** |
| WBC Count | 11200 cells/uL | 4000-11000 | **high** |
| Platelet Count | 210000 cells/uL | 150000-450000 | normal |
| Creatinine | 1.8 mg/dL | 0.7-1.3 | **high** |
| Total Cholesterol | 245 mg/dL | 125-200 | **high** |

Expected result: **5 of 6 values flagged abnormal**, only Platelet Count normal.

## What's included

- `app/modules/medical_reports/`:
  - `reference_ranges.py` — **new file**: the 12-test reference range table
  - `ocr_engine.py` — **new file**: Tesseract wrapper + regex value extraction
  - `analyzer.py` — **new file**: rule-based abnormal-value flagging + summary generation
  - `models_analysis.py` — **new file**: `ReportOCRResult`, `ReportAnalysis` tables
  - `schemas_analysis.py` — **new file**
  - `repository_analysis.py` — **new file**
  - `service_analysis.py` — **new file**: orchestrates OCR → analysis → persistence, with the same RBAC pattern as the rest of `medical_reports`
  - `router.py` — **overwrite**: adds the 2 new endpoints below (includes all previous upload/list/download endpoints too)

## New endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/v1/reports/{report_id}/analyze` | Bearer (owner patient or assigned doctor) | Run OCR + analysis on an uploaded report (JPG/PNG only) |
| GET | `/v1/reports/{report_id}/analysis` | Bearer (owner patient or assigned doctor) | Fetch previously-computed results |

## How to apply

1. Install Tesseract OCR (see step 1 above) and set `TESSERACT_CMD` in `.env` if on Windows.
2. Add to `requirements/base.txt`:
   ```
   pytesseract==0.3.13
   pillow==10.4.0
   ```
   Then: `pip install pytesseract==0.3.13 pillow==10.4.0`
3. Add the 7 new files to `backend/app/modules/medical_reports/`, overwrite `router.py`.
4. **Register the new models with Alembic** — open `backend/alembic/env.py` and add:
   ```python
   from app.modules.medical_reports.models_analysis import ReportOCRResult, ReportAnalysis  # noqa: F401
   ```
5. Migrate:
   ```powershell
   cd backend
   venv\Scripts\activate
   alembic revision --autogenerate -m "add report_ocr_results and report_analysis tables"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

## How to test in Swagger UI

1. **Upload the test image**: `POST /v1/reports/upload` as patient → choose file → select `test-assets/sample_lab_report.png` → Execute. Note the returned `report_id`.
2. **Run analysis**: `POST /v1/reports/{report_id}/analyze` with that `report_id` → should return both `ocr_result` (extracted fields + raw OCR text) and `analysis` (5 abnormal values, a summary sentence, and next-steps text).
3. **Re-fetch without re-running**: `GET /v1/reports/{report_id}/analysis` → should return the same stored result instantly (no OCR re-run).
4. **RBAC test**: try analyzing a report that belongs to a different patient (as a doctor not assigned to them) → expect 403.
5. **Unsupported file type test**: if you have a PDF report uploaded from earlier testing, try analyzing it → expect a clear error message (PDF isn't supported by this implementation, documented above).

## Design notes

- **Idempotent re-analysis**: calling `/analyze` again on the same report updates the stored OCR/analysis records rather than creating duplicates (`upsert` pattern in the repository) — useful if you want to re-run after fixing something, without accumulating stale duplicate rows.
- **Deterministic rule engine as source of truth**: per the AI Pipeline doc's core requirement for this module, the abnormal/normal flag is always computed by the deterministic reference-range comparison in `analyzer.py` — the "summary" text is just a template rendering of that same data, so there's no possibility of the human-readable summary contradicting the underlying flags (which is the property that mattered in the original design, independent of the LLM-vs-template question).
