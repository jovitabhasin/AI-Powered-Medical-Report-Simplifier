# AI-Powered Medical Report Simplifier

## Overview

This project accepts either:

- typed medical report text
- a scanned or screenshot image of a report

It processes the report in the same 4 stages described in the problem statement:

1. OCR/Text Extraction
2. Normalized Tests JSON
3. Patient-Friendly Summary
4. Final Output

The API responses are intentionally kept aligned with the JSON formats shown in the assignment.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- EasyOCR

## Project Structure

```text
app/
  main.py
  schemas.py
  catalog.py
  services/
    cleanup.py
    extractor.py
    normalizer.py
    ocr.py
    summarizer.py
tests/
  test_api.py
postman/
  medical-report-simplifier.postman_collection.json
requirements.txt
```

## Setup Instructions

Choose any one environment setup below.

### Option 1: Conda Environment

Create and activate a Conda environment:

```bash
conda create -n med-simplifier python=3.12
conda activate med-simplifier
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Option 2: Python Virtual Environment in WSL


Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Option 3: Python Virtual Environment in Windows Command Prompt or PowerShell

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Notes

- OCR dependencies can take time to install because `EasyOCR` pulls ML libraries such as `torch`
- the first OCR request can also be slower because the OCR model loads on first use

### Run the server

```bash
uvicorn app.main:app --reload
```

### Open Swagger docs

```text
http://127.0.0.1:8000/docs
```

## Architecture

The backend is organized as a simple pipeline where each assignment step is mapped to a dedicated service.

### Flow

```text
Text or Image Input
        |
        v
Step 1: Extractor
  - OCR for image input
  - typo cleanup
  - raw test line extraction
        |
        v
Step 2: Normalizer
  - canonical test name mapping
  - value parsing
  - unit normalization
  - reference range attachment
        |
        v
Step 3: Summarizer
  - simple patient-friendly explanation
  - no hallucinated tests allowed
        |
        v
Step 4: Final Composer
  - combine normalized tests and summary
```

### Components

- `app/main.py`
  Defines FastAPI routes and request handling.
- `app/services/ocr.py`
  Runs OCR for uploaded image input using EasyOCR.
- `app/services/cleanup.py`
  Repairs common OCR mistakes such as `Hemglobin -> Hemoglobin` and `Hgh -> High`.
- `app/services/extractor.py`
  Extracts raw lab test strings from cleaned text.
- `app/services/normalizer.py`
  Converts raw extracted strings into structured JSON with `name`, `value`, `unit`, `status`, and `ref_range`.
- `app/services/summarizer.py`
  Generates conservative patient-friendly summaries and applies guardrails.
- `app/catalog.py`
  Stores the supported lab test catalog, aliases, units, and reference ranges.

### Guardrail

If the summary layer tries to mention tests not present in the normalized input, the service returns:

```json
{
  "status": "unprocessed",
  "reason": "hallucinated tests not present in input"
}
```

## Supported Tests

The built-in catalog currently supports:

- Hemoglobin
- WBC
- RBC
- Hematocrit
- MCV
- MCH
- MCHC
- Platelets
- Neutrophils
- Lymphocytes
- Monocytes
- Eosinophils
- Basophils
- Glucose
- Urea
- Creatinine
- Sodium
- Potassium
- Chloride
- Calcium

## API Usage Examples

### 1. Health Check

Endpoint:

```text
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### 2. Step 1: OCR/Text Extraction

Endpoint:

```text
POST /step1/extract
```

Text request body:

```json
{
  "text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
}
```

Text example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/step1/extract ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)\"}"
```

Image example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/step1/extract ^
  -F "file=@sample-report.png"
```

Response:

```json
{
  "tests_raw": [
    "Hemoglobin 10.2 g/dL (Low)",
    "WBC 11200 /uL (High)"
  ],
  "confidence": 0.8
}
```

### 3. Step 2: Normalized Tests JSON

Endpoint:

```text
POST /step2/normalize
```

Request body:

```json
{
  "tests_raw": [
    "Hemoglobin 10.2 g/dL (Low)",
    "WBC 11200 /uL (High)"
  ]
}
```

Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/step2/normalize ^
  -H "Content-Type: application/json" ^
  -d "{\"tests_raw\":[\"Hemoglobin 10.2 g/dL (Low)\",\"WBC 11200 /uL (High)\"]}"
```

Response:

```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {
        "low": 12.0,
        "high": 15.0
      }
    },
    {
      "name": "WBC",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {
        "low": 4000,
        "high": 11000
      }
    }
  ],
  "normalization_confidence": 0.99
}
```

### 4. Step 3: Patient-Friendly Summary

Endpoint:

```text
POST /step3/summarize
```

Request body:

```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {
        "low": 12.0,
        "high": 15.0
      }
    },
    {
      "name": "WBC",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {
        "low": 4000,
        "high": 11000
      }
    }
  ]
}
```

Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/step3/summarize ^
  -H "Content-Type: application/json" ^
  -d "{\"tests\":[{\"name\":\"Hemoglobin\",\"value\":10.2,\"unit\":\"g/dL\",\"status\":\"low\",\"ref_range\":{\"low\":12.0,\"high\":15.0}},{\"name\":\"WBC\",\"value\":11200,\"unit\":\"/uL\",\"status\":\"high\",\"ref_range\":{\"low\":4000,\"high\":11000}}]}"
```

Response:

```json
{
  "summary": "Low hemoglobin and high white blood cell count.",
  "explanations": [
    "Low hemoglobin may relate to anemia.",
    "High WBC can occur with infections."
  ]
}
```

### 5. Step 4: Final Output

Endpoint:

```text
POST /step4/final
```

Request body:

```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {
        "low": 12.0,
        "high": 15.0
      }
    },
    {
      "name": "WBC",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {
        "low": 4000,
        "high": 11000
      }
    }
  ],
  "summary": "Low hemoglobin and high white blood cell count."
}
```

Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/step4/final ^
  -H "Content-Type: application/json" ^
  -d "{\"tests\":[{\"name\":\"Hemoglobin\",\"value\":10.2,\"unit\":\"g/dL\",\"status\":\"low\",\"ref_range\":{\"low\":12.0,\"high\":15.0}},{\"name\":\"WBC\",\"value\":11200,\"unit\":\"/uL\",\"status\":\"high\",\"ref_range\":{\"low\":4000,\"high\":11000}}],\"summary\":\"Low hemoglobin and high white blood cell count.\"}"
```

Response:

```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL",
      "status": "low",
      "ref_range": {
        "low": 12.0,
        "high": 15.0
      }
    },
    {
      "name": "WBC",
      "value": 11200,
      "unit": "/uL",
      "status": "high",
      "ref_range": {
        "low": 4000,
        "high": 11000
      }
    }
  ],
  "summary": "Low hemoglobin and high white blood cell count.",
  "status": "ok"
}
```

### 6. Full Pipeline Convenience Endpoint

This endpoint is an extra helper endpoint added for easier testing. The assignment-aligned step endpoints still remain the primary implementation.

Endpoint:

```text
POST /pipeline/run
```

Request body:

```json
{
  "text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
}
```

Response:

```json
{
  "step1": {
    "tests_raw": [
      "Hemoglobin 10.2 g/dL (Low)",
      "WBC 11200 /uL (High)"
    ],
    "confidence": 1.0
  },
  "step2": {
    "tests": [
      {
        "name": "Hemoglobin",
        "value": 10.2,
        "unit": "g/dL",
        "status": "low",
        "ref_range": {
          "low": 12.0,
          "high": 15.0
        }
      },
      {
        "name": "WBC",
        "value": 11200,
        "unit": "/uL",
        "status": "high",
        "ref_range": {
          "low": 4000,
          "high": 11000
        }
      }
    ],
    "normalization_confidence": 0.99
  },
  "step3": {
    "summary": "Low hemoglobin and high white blood cell count.",
    "explanations": [
      "Low hemoglobin may relate to anemia.",
      "High WBC can occur with infections."
    ]
  },
  "step4": {
    "tests": [
      {
        "name": "Hemoglobin",
        "value": 10.2,
        "unit": "g/dL",
        "status": "low",
        "ref_range": {
          "low": 12.0,
          "high": 15.0
        }
      },
      {
        "name": "WBC",
        "value": 11200,
        "unit": "/uL",
        "status": "high",
        "ref_range": {
          "low": 4000,
          "high": 11000
        }
      }
    ],
    "summary": "Low hemoglobin and high white blood cell count.",
    "status": "ok"
  }
}
```

## Working Backend Demo with ngrok

The assignment allows submitting a working backend demo using a local server exposed through ngrok.

### 1. Start the FastAPI server locally

```bash
uvicorn app.main:app --reload
```

This runs the backend on:

```text
http://127.0.0.1:8000
```

### 2. Start ngrok in a separate terminal

```bash
ngrok http 8000
```

ngrok will generate a public forwarding URL similar to:

```text
https://example-name.ngrok-free.dev -> http://localhost:8000
```

### 3. Open the public Swagger docs

Append `/docs` to the generated ngrok URL:

```text
https://example-name.ngrok-free.dev/docs
```

