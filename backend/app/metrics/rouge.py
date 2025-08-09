from __future__ import annotations

try:
    from rouge_score import rouge_scorer  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    rouge_scorer = None


def rougeL(reference: str, prediction: str) -> float:
    if rouge_scorer is None:
        return 0.0
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = scorer.score(reference, prediction)
    return float(scores["rougeL"].fmeasure)