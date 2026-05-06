from __future__ import annotations

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas import (
    ErrorResponse,
    FinalInput,
    HealthResponse,
    PipelineRunResponse,
    RawTestsInput,
    Step1ExtractResponse,
    Step2NormalizeResponse,
    Step3SummarizeResponse,
    Step4FinalResponse,
    TestsInput,
    TextExtractionInput,
)
from app.services.extractor import ExtractorService
from app.services.normalizer import NormalizerService
from app.services.summarizer import SummarizerService


app = FastAPI(title="AI-Powered Medical Report Simplifier")

extractor_service = ExtractorService()
normalizer_service = NormalizerService()
summarizer_service = SummarizerService()


def invalid_input_response() -> JSONResponse:
    payload = ErrorResponse(status="error", reason="invalid_input")
    return JSONResponse(status_code=400, content=payload.model_dump())


STEP1_REQUEST_BODY = {
    "required": True,
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "title": "Text",
                    }
                },
                "required": ["text"],
            },
            "example": {
                "text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
            },
        },
        "multipart/form-data": {
            "schema": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    }
                },
                "required": ["file"],
            }
        },
    },
}


async def extract_request_payload(request: Request) -> Step1ExtractResponse | JSONResponse:
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("application/json"):
        try:
            payload = TextExtractionInput(**(await request.json()))
        except (ValidationError, ValueError):
            return invalid_input_response()
        return extractor_service.extract_from_text(payload.text)

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        if not upload or not hasattr(upload, "read"):
            return invalid_input_response()

        image_bytes = await upload.read()
        if not image_bytes:
            return invalid_input_response()

        try:
            return extractor_service.extract_from_image(image_bytes)
        except RuntimeError as exc:
            payload = ErrorResponse(status="error", reason=str(exc))
            return JSONResponse(status_code=500, content=payload.model_dump())

    return invalid_input_response()


def build_pipeline_response(step1: Step1ExtractResponse) -> PipelineRunResponse:
    if isinstance(step1, dict):
        step1 = Step1ExtractResponse(**step1)
    step2 = normalizer_service.normalize(step1.tests_raw)
    step3_result = summarizer_service.summarize(step2.tests)

    if isinstance(step3_result, ErrorResponse):
        return PipelineRunResponse(
            step1=step1,
            step2=step2,
            step3=step3_result,
            step4=step3_result,
        )

    step4 = Step4FinalResponse(
        tests=step2.tests,
        summary=step3_result.summary,
        status="ok",
    )
    return PipelineRunResponse(
        step1=step1,
        step2=step2,
        step3=step3_result,
        step4=step4,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/step1/extract",
    response_model=Step1ExtractResponse,
    openapi_extra={
        "requestBody": STEP1_REQUEST_BODY
    },
)
async def step1_extract(request: Request):
    return await extract_request_payload(request)


@app.post("/step2/normalize", response_model=Step2NormalizeResponse)
def step2_normalize(payload: RawTestsInput):
    return normalizer_service.normalize(payload.tests_raw)


@app.post("/step3/summarize")
def step3_summarize(payload: TestsInput):
    result = summarizer_service.summarize(payload.tests)
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=200, content=result.model_dump())
    response = Step3SummarizeResponse(
        summary=result.summary,
        explanations=result.explanations,
    )
    return response


@app.post("/step4/final", response_model=Step4FinalResponse)
def step4_final(payload: FinalInput):
    return Step4FinalResponse(
        tests=payload.tests,
        summary=payload.summary,
        status="ok",
    )


@app.post(
    "/pipeline/run",
    response_model=PipelineRunResponse,
    openapi_extra={
        "requestBody": STEP1_REQUEST_BODY
    },
)
async def pipeline_run(request: Request):
    step1 = await extract_request_payload(request)
    if isinstance(step1, JSONResponse):
        return step1
    return build_pipeline_response(step1)
