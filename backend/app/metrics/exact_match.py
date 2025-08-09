from __future__ import annotations

import re


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def exact_match(reference: str, prediction: str, input_text: str) -> float:  # input_text unused
    return 1.0 if _normalize(reference) == _normalize(prediction) else 0.0