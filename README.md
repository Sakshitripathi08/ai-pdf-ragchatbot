# AI PDF RAG Chatbot

A FastAPI starter for extracting text from PDFs, retrieving relevant passages with FAISS, and answering questions with an OpenAI-compatible chat model.

## Run locally

Requires Python 3.11 and a working C/C++ runtime for FAISS/ML dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY and a long random API_KEY in .env before exposing the service.
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. The first upload downloads the sentence-transformer model, so initial indexing can take time and needs network access.

## Docker deployment

1. Set strong, secret values for `API_KEY` and `OPENAI_API_KEY` in `.env`; do not commit `.env`.
2. Start with `docker compose up --build -d`.
3. Put a TLS-terminating reverse proxy/load balancer in front of the service before public exposure. Keep the service bound to localhost unless network ingress is intentionally configured.
4. Back up the `app_data` volume. The local FAISS index is single-instance storage; do not run multiple replicas against it. For horizontal scale, replace it with shared object storage and a managed vector database.

API requests need `Authorization: Bearer <API_KEY>` when `API_KEY` is configured. If no key is configured, API authentication is disabled; do not expose that configuration publicly.

## API

- `GET /health/live` — process liveness
- `GET /health/ready` — readiness
- `POST /api/upload` — multipart field `file`; default upload limit is 20 MiB
- `POST /api/chat` — JSON body `{"question":"..."}`

Example:

```bash
curl -H "Authorization: Bearer $API_KEY" -F "file=@document.pdf" http://127.0.0.1:8000/api/upload
curl -H "Authorization: Bearer $API_KEY" -H 'Content-Type: application/json' \
  -d '{"question":"What is this document about?"}' http://127.0.0.1:8000/api/chat
```

## Configuration

See `.env.example`. `MAX_UPLOAD_BYTES` controls the maximum accepted PDF size. `OPENAI_API_KEY` enables model-generated answers; without it, the API returns a relevant retrieved passage. Store secrets in your deployment platform's secret manager.

## Operational notes

This provides a safer single-instance deployment baseline, not a fully managed production platform. Before handling sensitive or high-volume workloads, add per-user authentication/authorization, rate limiting, malware scanning, retention/deletion workflows, monitoring and alerting, and external durable storage. Scanned PDFs require OCR, which is not included. PDF text and model output should be treated as untrusted content.
