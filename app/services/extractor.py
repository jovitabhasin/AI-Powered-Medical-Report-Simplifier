from __future__ import annotations

import re

from app.catalog import get_aliases, resolve_test_name
from app.schemas import Step1ExtractResponse
from app.services.cleanup import cleanup_text
from app.services.ocr import OCRService


def _alias_pattern() -> str:
    aliases = [re.escape(alias) for alias in get_aliases()]
    return "|".join(aliases)


TEST_PATTERN = re.compile(
    rf"(?P<name>{_alias_pattern()})\s*[:\-]?\s*"
    r"(?P<value>\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>(?:/?[A-Za-zµ]+(?:/[A-Za-zµ]+)?|%))?"
    r"\s*(?:\((?P<status>[A-Za-z]+)\))?",
    re.IGNORECASE,
)


UNIT_ALIASES = {
    "g/dl": "g/dL",
    "mg/dl": "mg/dL",
    "/ul": "/uL",
    "ul": "uL",
    "iul": "/uL",
    "lul": "/uL",
    "1ul": "/uL",
    "/uL": "/uL",
}


class ExtractorService:
    def __init__(self, ocr_service: OCRService | None = None) -> None:
        self.ocr_service = ocr_service or OCRService()

    def extract_from_text(self, text: str) -> Step1ExtractResponse:
        cleaned = cleanup_text(text)
        tests_raw, structure_confidence = self._extract_tests(cleaned)
        confidence = round(structure_confidence, 2)
        return Step1ExtractResponse(tests_raw=tests_raw, confidence=confidence)

    def extract_from_image(self, image_bytes: bytes) -> Step1ExtractResponse:
        raw_text, ocr_confidence = self.ocr_service.extract_text_from_image(image_bytes)
        cleaned = cleanup_text(raw_text)
        tests_raw, structure_confidence = self._extract_tests(cleaned)
        confidence = round((ocr_confidence + structure_confidence) / 2, 2) if tests_raw else 0.0
        return Step1ExtractResponse(tests_raw=tests_raw, confidence=confidence)

    def _extract_tests(self, text: str) -> tuple[list[str], float]:
        tests_raw: list[str] = []
        scores: list[float] = []

        for match in TEST_PATTERN.finditer(text):
            canonical_name = resolve_test_name(match.group("name") or "")
            if not canonical_name:
                continue

            value_text = self._normalize_value_text(match.group("value") or "")
            unit = self._normalize_unit(match.group("unit"))
            status = self._normalize_status(match.group("status"))

            parts = [canonical_name, value_text]
            if unit:
                parts.append(unit)
            line = " ".join(parts)
            if status:
                line = f"{line} ({status})"
            tests_raw.append(line)

            score = 0.7
            if unit:
                score += 0.15
            if status:
                score += 0.15
            scores.append(min(score, 1.0))

        if not tests_raw:
            return [], 0.0

        return tests_raw, sum(scores) / len(scores)

    @staticmethod
    def _normalize_value_text(value_text: str) -> str:
        normalized = value_text.replace(",", "")
        if "." in normalized:
            return normalized.rstrip("0").rstrip(".") if normalized.endswith("0") else normalized
        return normalized

    @staticmethod
    def _normalize_unit(unit: str | None) -> str:
        if not unit:
            return ""
        normalized = unit.strip()
        return UNIT_ALIASES.get(normalized.lower(), normalized)

    @staticmethod
    def _normalize_status(status: str | None) -> str:
        if not status:
            return ""
        status_lower = status.strip().lower()
        mapping = {"low": "Low", "high": "High", "normal": "Normal"}
        return mapping.get(status_lower, status_lower.capitalize())
