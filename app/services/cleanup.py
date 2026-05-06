from __future__ import annotations

import re


TYPO_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\bHemglobin\b", "Hemoglobin"),
    (r"\bHemglo?bin\b", "Hemoglobin"),
    (r"\bHgh\b", "High"),
    (r"\bL0w\b", "Low"),
    (r"\bVBC\b", "WBC"),
    (r"\bW8C\b", "WBC"),
    (r"\bW8c\b", "WBC"),
    (r"\bWB[Cc]\b", "WBC"),
    (r"\bWhlte\b", "White"),
    (r"\bCeunt\b", "Count"),
    (r"\b112OO\b", "11200"),
    (r"\bIuL\b", "/uL"),
    (r"\bluL\b", "/uL"),
    (r"\b1uL\b", "/uL"),
)


def cleanup_text(text: str) -> str:
    cleaned = text.replace("\r", "\n")
    for pattern, replacement in TYPO_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)
    return cleaned.strip()
