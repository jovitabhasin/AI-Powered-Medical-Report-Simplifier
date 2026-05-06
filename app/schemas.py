from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    status: str
    reason: str


class HealthResponse(BaseModel):
    status: str


class TextExtractionInput(BaseModel):
    text: str


class Step1ExtractResponse(BaseModel):
    tests_raw: list[str] = Field(default_factory=list)
    confidence: float


class RawTestsInput(BaseModel):
    tests_raw: list[str] = Field(default_factory=list)


class RefRange(BaseModel):
    low: int | float
    high: int | float


class NormalizedTest(BaseModel):
    name: str
    value: int | float
    unit: str
    status: str
    ref_range: RefRange


class Step2NormalizeResponse(BaseModel):
    tests: list[NormalizedTest] = Field(default_factory=list)
    normalization_confidence: float


class TestsInput(BaseModel):
    tests: list[NormalizedTest] = Field(default_factory=list)


class Step3SummarizeResponse(BaseModel):
    summary: str
    explanations: list[str] = Field(default_factory=list)


class FinalInput(BaseModel):
    tests: list[NormalizedTest] = Field(default_factory=list)
    summary: str


class Step4FinalResponse(BaseModel):
    tests: list[NormalizedTest] = Field(default_factory=list)
    summary: str
    status: str


class PipelineRunResponse(BaseModel):
    step1: Step1ExtractResponse
    step2: Step2NormalizeResponse
    step3: Step3SummarizeResponse | ErrorResponse
    step4: Step4FinalResponse | ErrorResponse
