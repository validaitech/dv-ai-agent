from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Dataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    storage_path: str
    num_items: int = 0


class EvaluationRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    dataset_id: int = Field(foreign_key="dataset.id")
    model_provider: str
    model_name: str
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 512
    metrics_json: str  # JSON-encoded list of metric names
    status: str = "pending"  # pending | running | completed | failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    aggregate_results_json: Optional[str] = None  # JSON-encoded dict
    num_items: int = 0
    error_message: Optional[str] = None


class EvaluationItemResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="evaluationrun.id")
    item_index: int
    input_text: str
    reference_text: Optional[str] = None
    output_text: Optional[str] = None
    scores_json: Optional[str] = None  # JSON-encoded dict