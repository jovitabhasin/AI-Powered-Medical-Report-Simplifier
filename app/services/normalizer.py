from __future__ import annotations

from app.catalog import LAB_TEST_CATALOG, resolve_test_name
from app.schemas import NormalizedTest, RefRange, Step2NormalizeResponse
from app.services.extractor import TEST_PATTERN, UNIT_ALIASES


class NormalizerService:
    def normalize(self, tests_raw: list[str]) -> Step2NormalizeResponse:
        normalized_tests: list[NormalizedTest] = []
        scores: list[float] = []

        for raw_test in tests_raw:
            match = TEST_PATTERN.search(raw_test)
            if not match:
                continue

            canonical_name = resolve_test_name(match.group("name") or "")
            if not canonical_name:
                continue

            entry = LAB_TEST_CATALOG[canonical_name]
            value = self._parse_value(match.group("value") or "")
            unit = self._normalize_unit(match.group("unit")) or entry.unit
            ref_range = RefRange(
                low=entry.ref_range["low"],
                high=entry.ref_range["high"],
            )
            status = self._normalize_status(match.group("status"), value, ref_range)

            normalized_tests.append(
                NormalizedTest(
                    name=canonical_name,
                    value=value,
                    unit=unit,
                    status=status,
                    ref_range=ref_range,
                )
            )
            scores.append(self._score_test(unit, entry.unit, match.group("status")))

        if not normalized_tests:
            return Step2NormalizeResponse(tests=[], normalization_confidence=0.0)

        normalization_confidence = round(sum(scores) / len(scores), 2)
        return Step2NormalizeResponse(
            tests=normalized_tests,
            normalization_confidence=normalization_confidence,
        )

    @staticmethod
    def _parse_value(value_text: str) -> int | float:
        cleaned = value_text.replace(",", "")
        return float(cleaned) if "." in cleaned else int(cleaned)

    @staticmethod
    def _normalize_unit(unit: str | None) -> str:
        if not unit:
            return ""
        normalized = unit.strip()
        return UNIT_ALIASES.get(normalized.lower(), normalized)

    @staticmethod
    def _normalize_status(status_text: str | None, value: int | float, ref_range: RefRange) -> str:
        if status_text:
            lowered = status_text.strip().lower()
            if lowered in {"low", "high", "normal"}:
                return lowered

        if value < ref_range.low:
            return "low"
        if value > ref_range.high:
            return "high"
        return "normal"

    @staticmethod
    def _score_test(unit: str, expected_unit: str, explicit_status: str | None) -> float:
        score = 0.6
        if unit == expected_unit:
            score += 0.2
        elif unit:
            score += 0.1
        if explicit_status:
            score += 0.1
        else:
            score += 0.05
        score += 0.09
        return min(score, 0.99)

