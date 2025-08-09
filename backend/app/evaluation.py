from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from sqlmodel import select

from .database import get_session
from .metrics import METRICS_REGISTRY
from .model_provider import ModelProvider
from .models import Dataset, EvaluationItemResult, EvaluationRun


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "datasets"


def _load_dataset_items(storage_path: str) -> List[Dict[str, str]]:
    path = Path(storage_path)
    items: List[Dict[str, str]] = []
    if path.suffix.lower() in {".jsonl", ".json"}:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                items.append({
                    "input": str(obj.get("input", "")),
                    "reference": str(obj.get("reference", "")) if obj.get("reference") is not None else "",
                })
    elif path.suffix.lower() == ".csv":
        import csv

        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                items.append({
                    "input": str(row.get("input", "")),
                    "reference": str(row.get("reference", "")) if row.get("reference") is not None else "",
                })
    else:
        raise ValueError("Unsupported dataset format. Use JSONL with keys 'input' and 'reference' or CSV with same headers.")
    return items


async def run_evaluation_async(run_id: int) -> None:
    # Load run configuration
    with get_session() as session:
        run = session.get(EvaluationRun, run_id)
        if run is None:
            return
        run.status = "running"
        run.updated_at = datetime.utcnow()
        session.add(run)
        session.commit()

    try:
        with get_session() as session:
            run = session.get(EvaluationRun, run_id)
            assert run is not None
            dataset = session.get(Dataset, run.dataset_id)
            assert dataset is not None
            items = _load_dataset_items(dataset.storage_path)

        metrics = json.loads(run.metrics_json)
        provider = ModelProvider(
            provider=run.model_provider,
            model_name=run.model_name,
            temperature=run.temperature,
            top_p=run.top_p,
            max_tokens=run.max_tokens,
        )

        metric_sums: Dict[str, float] = {name: 0.0 for name in metrics}
        samples: List[Dict] = []

        # Simple sequential loop with small concurrency for API providers
        semaphore = asyncio.Semaphore(4)

        async def process_item(index: int, input_text: str, reference_text: str) -> None:
            nonlocal metric_sums
            async with semaphore:
                output_text = await asyncio.to_thread(provider.generate, input_text)
                scores: Dict[str, float] = {}
                for m in metrics:
                    fn = METRICS_REGISTRY.get(m)
                    if not fn:
                        continue
                    try:
                        s = await asyncio.to_thread(fn, reference_text, output_text)
                    except Exception:
                        s = 0.0
                    scores[m] = float(s)
                    metric_sums[m] += float(s)
                with get_session() as s:
                    s.add(EvaluationItemResult(
                        run_id=run_id,
                        item_index=index,
                        input_text=input_text,
                        reference_text=reference_text or None,
                        output_text=output_text,
                        scores_json=json.dumps(scores),
                    ))
                    s.commit()

        tasks: List[asyncio.Task] = []
        for idx, item in enumerate(items):
            tasks.append(asyncio.create_task(process_item(idx, item.get("input", ""), item.get("reference", ""))))
        await asyncio.gather(*tasks)

        # Aggregate
        aggregate = {name: metric_sums[name] / max(len(items), 1) for name in metrics}

        with get_session() as session:
            run = session.get(EvaluationRun, run_id)
            assert run is not None
            run.status = "completed"
            run.updated_at = datetime.utcnow()
            run.aggregate_results_json = json.dumps(aggregate)
            run.num_items = len(items)
            session.add(run)
            session.commit()

    except Exception as e:  # pragma: no cover
        with get_session() as session:
            run = session.get(EvaluationRun, run_id)
            if run is None:
                return
            run.status = "failed"
            run.error_message = str(e)
            run.updated_at = datetime.utcnow()
            session.add(run)
            session.commit()