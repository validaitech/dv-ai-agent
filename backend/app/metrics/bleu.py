from __future__ import annotations

from typing import List

try:
    import sacrebleu  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    sacrebleu = None


def bleu(reference: str, prediction: str) -> float:
    if sacrebleu is None:
        return 0.0
    # sacrebleu expects list of references
    bleu_obj = sacrebleu.corpus_bleu([prediction], [[reference]])
    return float(bleu_obj.score) / 100.0