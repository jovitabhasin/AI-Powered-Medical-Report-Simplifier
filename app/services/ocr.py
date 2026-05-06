from __future__ import annotations

from functools import lru_cache
from io import BytesIO


class OCRService:
    def extract_text_from_image(self, image_bytes: bytes) -> tuple[str, float]:
        try:
            import numpy as np
            from PIL import Image
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "easyocr_dependencies_missing"
            ) from exc

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image_array = np.array(image)
        reader = self._get_reader(easyocr)
        results = reader.readtext(image_array, detail=1, paragraph=False)

        lines: list[str] = []
        scores: list[float] = []
        for _, text, score in results:
            if text.strip():
                lines.append(text.strip())
                scores.append(max(0.0, min(float(score), 1.0)))

        combined_text = "\n".join(lines).strip()
        if not scores:
            return combined_text, 0.0

        average_score = round(sum(scores) / len(scores), 2)
        return combined_text, average_score

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_reader(easyocr_module):
        return easyocr_module.Reader(["en"], gpu=False)

