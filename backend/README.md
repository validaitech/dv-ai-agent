# LLM Checks - Evaluation Service

A minimal evaluation service inspired by Deepchecks, focused on LLM generation tasks. Supports dataset upload (JSONL/CSV), running evaluations against multiple providers (Gemini, LiteLLM/OpenAI, HuggingFace), standard text metrics (Exact Match, ROUGE-L, BLEU), and LLM-judge evaluations (relevance, hallucination, toxicity, bias, precision, recall, task completion, correctness, confidence, and data validation).

## Features
- Upload datasets (`input`, `reference`) as JSONL or CSV
- Providers: **Gemini** (default), LiteLLM/OpenAI, HuggingFace
- Metrics: Exact Match, ROUGE-L, BLEU, and judge-based: answer_relevancy, hallucinations, toxicity, biasness, precision, recall, task_completion, correctness, confidence_score, data_validation
- Async background execution with per-item and aggregate results persisted in PostgreSQL
- REST API via FastAPI

## Setup

1. Create `.env` from example and adjust values
```bash
cp .env.example .env
# Set GEMINI_API_KEY
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

## Use Gemini (free tier)
- Get an API key from Google AI Studio and set `GEMINI_API_KEY` in `.env`.
- Default provider/model are `gemini` and `gemini-1.5-flash`. You can override per-run via API.

## API
- Health: GET http://localhost:8000/health
- Metrics: GET http://localhost:8000/metrics
- Upload dataset: POST http://localhost:8000/datasets (multipart form: `file`, optional `name`)
- Create evaluation: POST http://localhost:8000/evaluations
```json
{
  "name": "demo",
  "dataset_id": 1,
  "model_provider": "gemini",
  "model_name": "gemini-1.5-flash",
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
- Judge metrics use the judge provider/model (`JUDGE_PROVIDER`/`JUDGE_MODEL`), defaulting to Gemini.
- You can still use LiteLLM/OpenAI by setting `LLM_PROVIDER=litellm` and the appropriate key.
- Local HuggingFace models require `transformers` and potentially `torch`.