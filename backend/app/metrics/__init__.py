from __future__ import annotations

from typing import Callable, Dict

from .exact_match import exact_match
from .bleu import bleu
from .rouge import rougeL

MetricFunction = Callable[[str, str], float]

METRICS_REGISTRY: Dict[str, MetricFunction] = {
    "exact_match": exact_match,
    "bleu": bleu,
    "rougeL": rougeL,
}


def available_metrics() -> Dict[str, str]:
    return {
        "exact_match": "Strict normalized string match",
        "bleu": "SacreBLEU score",
        "rougeL": "ROUGE-L F1 score",
    }