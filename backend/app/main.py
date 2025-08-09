from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import select

from .database import get_session, init_db
from .evaluation import run_evaluation_async
from .metrics import available_metrics
from .models import Dataset, EvaluationItemResult, EvaluationRun
from .schemas import (
    DatasetCreateResponse,
    DatasetInfo,
    EvaluationCreateRequest,
    EvaluationCreateResponse,
    EvaluationItemScore,
    EvaluationResultsResponse,
    EvaluationStatusResponse,
)

app = FastAPI(title="LLM Checks - Evaluation Service")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("data/datasets").mkdir(parents=True, exist_ok=True)
    init_db()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def list_metrics() -> dict:
    return available_metrics()


@app.post("/datasets", response_model=DatasetCreateResponse)
async def upload_dataset(file: UploadFile = File(...), name: str = "dataset"):
    filename = file.filename or "dataset.jsonl"
    ext = Path(filename).suffix.lower()
    if ext not in {".jsonl", ".json", ".csv"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .jsonl or .csv")
    storage_path = Path("data/datasets") / f"{int(datetime.utcnow().timestamp())}_{filename}"
    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)

    # Count items quickly
    num_items = 0
    if ext in {".jsonl", ".json"}:
        for line in io.BytesIO(content).read().decode("utf-8").splitlines():
            if line.strip():
                num_items += 1
    else:
        num_items = max(0, io.BytesIO(content).read().decode("utf-8").count("\n") - 1)

    with get_session() as session:
        ds = Dataset(name=name, storage_path=str(storage_path), num_items=num_items)
        session.add(ds)
        session.commit()
        session.refresh(ds)
        return DatasetCreateResponse(dataset_id=ds.id, name=ds.name, num_items=ds.num_items)


@app.get("/datasets", response_model=List[DatasetInfo])
async def list_datasets():
    with get_session() as session:
        datasets = session.exec(select(Dataset)).all()
        return [DatasetInfo(id=d.id, name=d.name, description=d.description, num_items=d.num_items) for d in datasets]


@app.post("/evaluations", response_model=EvaluationCreateResponse)
async def create_evaluation(req: EvaluationCreateRequest, background_tasks: BackgroundTasks):
    metrics_json = json.dumps(req.metrics)
    with get_session() as session:
        run = EvaluationRun(
            name=req.name,
            dataset_id=req.dataset_id,
            model_provider=req.model_provider,
            model_name=req.model_name,
            temperature=req.temperature,
            top_p=req.top_p,
            max_tokens=req.max_tokens,
            metrics_json=metrics_json,
            status="pending",
        )
        session.add(run)
        session.commit()
        session.refresh(run)

    background_tasks.add_task(run_evaluation_async, run.id)
    return EvaluationCreateResponse(run_id=run.id, status="pending")


@app.get("/evaluations/{run_id}", response_model=EvaluationStatusResponse)
async def get_evaluation_status(run_id: int):
    with get_session() as session:
        run = session.get(EvaluationRun, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        metrics = json.loads(run.metrics_json)
        aggregate = json.loads(run.aggregate_results_json) if run.aggregate_results_json else None
        return EvaluationStatusResponse(
            run_id=run.id,
            status=run.status,
            num_items=run.num_items,
            metrics=metrics,
            aggregate_results=aggregate,
            error_message=run.error_message,
        )


@app.get("/evaluations/{run_id}/results", response_model=EvaluationResultsResponse)
async def get_evaluation_results(run_id: int):
    with get_session() as session:
        run = session.get(EvaluationRun, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        if run.status != "completed":
            raise HTTPException(status_code=400, detail=f"Run not completed. Current status: {run.status}")
        metrics = json.loads(run.metrics_json)
        aggregate = json.loads(run.aggregate_results_json) if run.aggregate_results_json else {}
        items = session.exec(select(EvaluationItemResult).where(EvaluationItemResult.run_id == run_id)).all()
        samples = []
        for it in items[:100]:  # cap
            samples.append(
                EvaluationItemScore(
                    item_index=it.item_index,
                    input_text=it.input_text,
                    reference_text=it.reference_text,
                    output_text=it.output_text,
                    scores=json.loads(it.scores_json or "{}"),
                )
            )
        return EvaluationResultsResponse(run_id=run.id, metrics=metrics, aggregate_results=aggregate, samples=samples)