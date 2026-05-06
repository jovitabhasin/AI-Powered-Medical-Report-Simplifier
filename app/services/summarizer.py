from __future__ import annotations

from app.catalog import LAB_TEST_CATALOG
from app.schemas import ErrorResponse, NormalizedTest, Step3SummarizeResponse


class SummarizerService:
    def summarize(self, tests: list[NormalizedTest]) -> Step3SummarizeResponse | ErrorResponse:
        if not tests:
            return ErrorResponse(
                status="unprocessed",
                reason="hallucinated tests not present in input",
            )
        payload, referenced_names = self.generate_summary_payload(tests)
        if not self.validate_provenance(tests, referenced_names):
            return ErrorResponse(
                status="unprocessed",
                reason="hallucinated tests not present in input",
            )
        return Step3SummarizeResponse(**payload)

    def generate_summary_payload(self, tests: list[NormalizedTest]) -> tuple[dict[str, object], list[str]]:
        abnormal_tests = [test for test in tests if test.status != "normal"]
        relevant_tests = abnormal_tests or tests

        summary_phrases: list[str] = []
        explanations: list[str] = []
        referenced_names: list[str] = []

        for test in relevant_tests:
            entry = LAB_TEST_CATALOG.get(test.name)
            status = test.status
            referenced_names.append(test.name)

            if entry:
                summary_phrases.append(entry.summary_phrases.get(status, f"{status} {test.name.lower()}"))
                explanations.append(
                    entry.explanations.get(
                        status,
                        f"{test.name} is marked as {status} in this report.",
                    )
                )
            else:
                summary_phrases.append(f"{status} {test.name.lower()}")
                explanations.append(f"{test.name} is marked as {status} in this report.")

        summary = self._join_summary_phrases(summary_phrases)
        return {"summary": summary, "explanations": explanations}, referenced_names

    @staticmethod
    def validate_provenance(tests: list[NormalizedTest], referenced_names: list[str]) -> bool:
        input_names = {test.name for test in tests}
        return set(referenced_names).issubset(input_names)

    @staticmethod
    def _join_summary_phrases(phrases: list[str]) -> str:
        if not phrases:
            return "No test findings could be summarized."
        if len(phrases) == 1:
            return f"{phrases[0].capitalize()}."
        if len(phrases) == 2:
            return f"{phrases[0].capitalize()} and {phrases[1]}."
        leading = ", ".join(phrases[:-1])
        return f"{leading.capitalize()}, and {phrases[-1]}."
