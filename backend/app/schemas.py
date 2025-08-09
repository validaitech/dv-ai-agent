from __future__ import annotations

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class DatasetCreateResponse(BaseModel):
    dataset_id: int
    name: str
    num_items: int


class DatasetInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    num_items: int


class EvaluationCreateRequest(BaseModel):
    name: str = Field(description="A friendly name for the evaluation run")
    dataset_id: int
    model_provider: Literal["openai", "litellm", "huggingface"] = "litellm"
    model_name: str
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 512
    metrics: List[str] = Field(default_factory=lambda: ["exact_match", "rougeL", "bleu"])


class EvaluationCreateResponse(BaseModel):
    run_id: int
    status: str


class EvaluationStatusResponse(BaseModel):
    run_id: int
    status: str
    num_items: int
    metrics: List[str]
    aggregate_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class EvaluationItemScore(BaseModel):
    item_index: int
    input_text: str
    reference_text: Optional[str] = None
    output_text: Optional[str] = None
    scores: Dict[str, float]


class EvaluationResultsResponse(BaseModel):
    run_id: int
    metrics: List[str]
    aggregate_results: Dict[str, float]
    samples: List[EvaluationItemScore]