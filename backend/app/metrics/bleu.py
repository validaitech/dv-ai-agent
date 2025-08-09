from __future__ import annotations

try:
    import sacrebleu  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    sacrebleu = None


def bleu(reference: str, prediction: str, input_text: str) -> float:  # input_text unused
    if sacrebleu is None:
        return 0.0
    bleu_obj = sacrebleu.corpus_bleu([prediction], [[reference]])
    return float(bleu_obj.score) / 100.0