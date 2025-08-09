# LLM Checks - Evaluation Service

A minimal evaluation service inspired by Deepchecks, focused on LLM generation tasks. Supports dataset upload (JSONL/CSV), running evaluations against multiple providers via LiteLLM/OpenAI or local HuggingFace models, and computing standard text metrics (Exact Match, ROUGE-L, BLEU), as well as LLM-judge evaluations (relevance, hallucination, toxicity, bias, precision, recall, task completion, correctness, confidence, and data validation).

## Features
- Upload datasets (`input`, `reference`) as JSONL or CSV
- Configure model provider (`litellm` / `openai` / `huggingface`) and model name
- Metrics: Exact Match, ROUGE-L, BLEU, and judge-based: answer_relevancy, hallucinations, toxicity, biasness, precision, recall, task_completion, correctness, confidence_score, data_validation
- Async background execution with per-item and aggregate results persisted in PostgreSQL
- REST API via FastAPI

## Setup

1. Create `.env` from example and adjust values
```bash
cp .env.example .env
```

2. Create and activate a Python environment
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Ensure PostgreSQL is running and `DATABASE_URL` is reachable (default: `postgresql+psycopg://postgres:postgres@localhost:5432/llmchecks`). Create the database if needed.

4. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API
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
  "metrics": [
    "exact_match", "rougeL", "bleu",
    "answer_relevancy", "hallucinations", "toxicity", "biasness",
    "precision", "recall", "task_completion", "correctness", "confidence_score", "data_validation"
  ]
}
```
- Check status: GET http://localhost:8000/evaluations/{run_id}
- Fetch results: GET http://localhost:8000/evaluations/{run_id}/results

## Notes
- Judge metrics use a separate judge model configured via `JUDGE_PROVIDER`/`JUDGE_MODEL`.
- For toxicity/bias, optional classical classifiers can be added; current implementation uses LLM judging.
- Local HuggingFace models require `transformers` and potentially `torch`.