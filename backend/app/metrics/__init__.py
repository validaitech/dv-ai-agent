from __future__ import annotations

from typing import Callable, Dict

from .exact_match import exact_match
from .bleu import bleu
from .rouge import rougeL
from .llm_judge import (
    relevance,
    hallucination,
    toxicity,
    bias,
    precision,
    recall,
    task_completion,
    correctness,
    confidence_score,
    data_validation,
)

# Metric function takes (reference, prediction, input_text)
MetricFunction = Callable[[str, str, str], float]

METRICS_REGISTRY: Dict[str, MetricFunction] = {
    "exact_match": exact_match,
    "bleu": bleu,
    "rougeL": rougeL,
    # LLM-judge driven metrics
    "answer_relevancy": relevance,
    "hallucinations": hallucination,
    "toxicity": toxicity,
    "biasness": bias,
    "precision": precision,
    "recall": recall,
    "task_completion": task_completion,
    "correctness": correctness,
    "confidence_score": confidence_score,
    "data_validation": data_validation,
}


def available_metrics() -> Dict[str, str]:
    return {
        "exact_match": "Strict normalized string match",
        "bleu": "SacreBLEU score",
        "rougeL": "ROUGE-L F1 score",
        "answer_relevancy": "LLM judge: does the answer address the input?",
        "hallucinations": "LLM judge: presence of unsupported claims",
        "toxicity": "LLM judge (or detoxify if installed): offensive content",
        "biasness": "LLM judge: harmful bias or stereotypes",
        "precision": "LLM judge: proportion of correct content",
        "recall": "LLM judge: coverage of key points from reference",
        "task_completion": "LLM judge: did it complete the requested task",
        "correctness": "LLM judge: factual/semantic correctness vs reference",
        "confidence_score": "LLM judge: estimated confidence of the answer",
        "data_validation": "JSON/format validation or LLM judge if schema unknown",
    }