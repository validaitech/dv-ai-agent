# LLM Checks - Evaluation Service

A minimal evaluation service inspired by Deepchecks, focused on LLM generation tasks. Supports dataset upload (JSONL/CSV), running evaluations against multiple providers via LiteLLM/OpenAI or local HuggingFace models, and computing standard text metrics (Exact Match, ROUGE-L, BLEU).

## Features
- Upload datasets (`input`, `reference`) as JSONL or CSV
- Configure model provider (`litellm` / `openai` / `huggingface`) and model name
- Compute metrics: Exact Match, ROUGE-L, BLEU
- Async background execution with per-item and aggregate results persisted in SQLite
- REST API via FastAPI

## Quickstart

1. Create and activate a Python environment (recommended)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set provider credentials (examples)

```bash
# For OpenAI / LiteLLM compatible providers
export OPENAI_API_KEY=sk-...
```

3. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Use the API
- Health: GET http://localhost:8000/health
- Metrics: GET http://localhost:8000/metrics
- Upload dataset: POST http://localhost:8000/datasets (multipart form: `file`, optional `name`)
- Create evaluation: POST http://localhost:8000/evaluations
```json
{
  "name": "demo",
  "dataset_id": 1,
  "model_provider": "litellm",
  "model_name": "gpt-4o-mini",
  "temperature": 0.0,
  "top_p": 1.0,
  "max_tokens": 256,
  "metrics": ["exact_match", "rougeL", "bleu"]
}
```
- Check status: GET http://localhost:8000/evaluations/{run_id}
- Fetch results: GET http://localhost:8000/evaluations/{run_id}/results

## Dataset format
- JSONL with objects: `{ "input": "...", "reference": "..." }`
- CSV with headers: `input,reference`

## Notes
- BLEU and ROUGE depend on optional packages; they are included.
- Local HuggingFace models require `transformers` (and possibly `torch`). Install as needed and use `"model_provider": "huggingface"` with `model_name` like `gpt2`.
- Results are stored in `backend/data/app.db` and datasets in `backend/data/datasets/`.