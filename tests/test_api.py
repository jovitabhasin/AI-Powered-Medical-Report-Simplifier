from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, summarizer_service


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_step1_extract_text_matches_assignment_shape() -> None:
    response = client.post(
        "/step1/extract",
        json={"text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tests_raw": [
            "Hemoglobin 10.2 g/dL (Low)",
            "WBC 11200 /uL (High)",
        ],
        "confidence": 1.0,
    }


def test_step1_extract_text_repairs_common_ocr_wbc_variants() -> None:
    response = client.post(
        "/step1/extract",
        json={"text": "CBC: Hemglobin 10.2 g/dL (Low) VBC 11200 IuL (Hgh)"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tests_raw": [
            "Hemoglobin 10.2 g/dL (Low)",
            "WBC 11200 /uL (High)",
        ],
        "confidence": 1.0,
    }


def test_step1_extract_image_uses_mocked_ocr(monkeypatch) -> None:
    def fake_extract_from_image(_: bytes):
        return {
            "tests_raw": [
                "Hemoglobin 10.2 g/dL (Low)",
                "WBC 11200 /uL (High)",
            ],
            "confidence": 0.8,
        }

    monkeypatch.setattr("app.main.extractor_service.extract_from_image", fake_extract_from_image)

    response = client.post(
        "/step1/extract",
        files={"file": ("report.png", b"fake-image-bytes", "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tests_raw": [
            "Hemoglobin 10.2 g/dL (Low)",
            "WBC 11200 /uL (High)",
        ],
        "confidence": 0.8,
    }


def test_step2_normalize_matches_assignment_shape() -> None:
    response = client.post(
        "/step2/normalize",
        json={
            "tests_raw": [
                "Hemoglobin 10.2 g/dL (Low)",
                "WBC 11200 /uL (High)",
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "tests": [
            {
                "name": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "status": "low",
                "ref_range": {"low": 12.0, "high": 15.0},
            },
            {
                "name": "WBC",
                "value": 11200,
                "unit": "/uL",
                "status": "high",
                "ref_range": {"low": 4000, "high": 11000},
            },
        ],
        "normalization_confidence": 0.99,
    }


def test_step2_normalize_supports_expanded_catalog_entries() -> None:
    response = client.post(
        "/step2/normalize",
        json={
            "tests_raw": [
                "MCV 72 fL (Low)",
                "Sodium 148 mEq/L (High)",
                "Neutrophils 78 % (High)",
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "tests": [
            {
                "name": "MCV",
                "value": 72,
                "unit": "fL",
                "status": "low",
                "ref_range": {"low": 80.0, "high": 100.0},
            },
            {
                "name": "Sodium",
                "value": 148,
                "unit": "mEq/L",
                "status": "high",
                "ref_range": {"low": 135.0, "high": 145.0},
            },
            {
                "name": "Neutrophils",
                "value": 78,
                "unit": "%",
                "status": "high",
                "ref_range": {"low": 40.0, "high": 70.0},
            },
        ],
        "normalization_confidence": 0.99,
    }


def test_step3_summarize_matches_assignment_shape() -> None:
    response = client.post(
        "/step3/summarize",
        json={
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "status": "low",
                    "ref_range": {"low": 12.0, "high": 15.0},
                },
                {
                    "name": "WBC",
                    "value": 11200,
                    "unit": "/uL",
                    "status": "high",
                    "ref_range": {"low": 4000, "high": 11000},
                },
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": "Low hemoglobin and high white blood cell count.",
        "explanations": [
            "Low hemoglobin may relate to anemia.",
            "High WBC can occur with infections.",
        ],
    }


def test_step4_final_matches_assignment_shape() -> None:
    response = client.post(
        "/step4/final",
        json={
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "status": "low",
                    "ref_range": {"low": 12.0, "high": 15.0},
                },
                {
                    "name": "WBC",
                    "value": 11200,
                    "unit": "/uL",
                    "status": "high",
                    "ref_range": {"low": 4000, "high": 11000},
                },
            ],
            "summary": "Low hemoglobin and high white blood cell count.",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "tests": [
            {
                "name": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "status": "low",
                "ref_range": {"low": 12.0, "high": 15.0},
            },
            {
                "name": "WBC",
                "value": 11200,
                "unit": "/uL",
                "status": "high",
                "ref_range": {"low": 4000, "high": 11000},
            },
        ],
        "summary": "Low hemoglobin and high white blood cell count.",
        "status": "ok",
    }


def test_pipeline_run_returns_intermediate_and_final_outputs() -> None:
    response = client.post(
        "/pipeline/run",
        json={"text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "step1": {
            "tests_raw": [
                "Hemoglobin 10.2 g/dL (Low)",
                "WBC 11200 /uL (High)",
            ],
            "confidence": 1.0,
        },
        "step2": {
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "status": "low",
                    "ref_range": {"low": 12.0, "high": 15.0},
                },
                {
                    "name": "WBC",
                    "value": 11200,
                    "unit": "/uL",
                    "status": "high",
                    "ref_range": {"low": 4000, "high": 11000},
                },
            ],
            "normalization_confidence": 0.99,
        },
        "step3": {
            "summary": "Low hemoglobin and high white blood cell count.",
            "explanations": [
                "Low hemoglobin may relate to anemia.",
                "High WBC can occur with infections.",
            ],
        },
        "step4": {
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "status": "low",
                    "ref_range": {"low": 12.0, "high": 15.0},
                },
                {
                    "name": "WBC",
                    "value": 11200,
                    "unit": "/uL",
                    "status": "high",
                    "ref_range": {"low": 4000, "high": 11000},
                },
            ],
            "summary": "Low hemoglobin and high white blood cell count.",
            "status": "ok",
        },
    }


def test_pipeline_run_image_uses_mocked_ocr(monkeypatch) -> None:
    def fake_extract_from_image(_: bytes):
        return {
            "tests_raw": [
                "Hemoglobin 10.2 g/dL (Low)",
                "WBC 11200 /uL (High)",
            ],
            "confidence": 0.8,
        }

    monkeypatch.setattr("app.main.extractor_service.extract_from_image", fake_extract_from_image)

    response = client.post(
        "/pipeline/run",
        files={"file": ("report.png", b"fake-image-bytes", "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["step1"] == {
        "tests_raw": [
            "Hemoglobin 10.2 g/dL (Low)",
            "WBC 11200 /uL (High)",
        ],
        "confidence": 0.8,
    }


def test_step3_guardrail_returns_exact_assignment_shape(monkeypatch) -> None:
    original_generator = summarizer_service.generate_summary_payload

    def fake_generator(tests):
        payload, _ = original_generator(tests)
        return payload, ["Hemoglobin", "Platelets"]

    monkeypatch.setattr(summarizer_service, "generate_summary_payload", fake_generator)

    response = client.post(
        "/step3/summarize",
        json={
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "status": "low",
                    "ref_range": {"low": 12.0, "high": 15.0},
                }
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "unprocessed",
        "reason": "hallucinated tests not present in input",
    }


def test_pipeline_run_returns_guardrail_in_step3_and_step4(monkeypatch) -> None:
    original_generator = summarizer_service.generate_summary_payload

    def fake_generator(tests):
        payload, _ = original_generator(tests)
        return payload, ["Hemoglobin", "Platelets"]

    monkeypatch.setattr(summarizer_service, "generate_summary_payload", fake_generator)

    response = client.post(
        "/pipeline/run",
        json={"text": "Hemoglobin 10.2 g/dL (Low)"},
    )

    assert response.status_code == 200
    assert response.json()["step3"] == {
        "status": "unprocessed",
        "reason": "hallucinated tests not present in input",
    }
    assert response.json()["step4"] == {
        "status": "unprocessed",
        "reason": "hallucinated tests not present in input",
    }


def test_pipeline_run_returns_assignment_guardrail_for_unknown_input() -> None:
    response = client.post(
        "/pipeline/run",
        json={"text": "XYZMarker 52 U/L (High)"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "step1": {
            "tests_raw": [],
            "confidence": 0.0,
        },
        "step2": {
            "tests": [],
            "normalization_confidence": 0.0,
        },
        "step3": {
            "status": "unprocessed",
            "reason": "hallucinated tests not present in input",
        },
        "step4": {
            "status": "unprocessed",
            "reason": "hallucinated tests not present in input",
        },
    }
