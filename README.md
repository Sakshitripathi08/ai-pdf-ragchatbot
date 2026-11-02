# AI PDF RAG Chatbot

A FastAPI app that extracts PDF text, retrieves relevant passages with FAISS, and answers questions with an OpenAI-compatible chat model.

## Deploy to Render

This repository includes a Render Blueprint in `render.yaml`.

1. Push this repository to GitHub and sign in to [Render](https://render.com/).
2. In Render, choose **New → Blueprint**, connect `SakshiCpp/ai-pdf-ragchatbot`, and apply the Blueprint.
3. Render creates a Docker web service, a persistent disk mounted at `/data`, and a generated `API_KEY`. Enter your `OPENAI_API_KEY` in the Blueprint prompt/dashboard if you want model-generated answers. Keep it secret.
4. Wait for the first build and deploy to finish. The first PDF upload initializes/downloads the sentence-transformer model, so allow extra time and ensure outbound network access.
5. Open the service's `onrender.com` URL. In the app, paste the service's `API_KEY` (Render Dashboard → service → Environment) into the access-key field. The key is held only in the current browser tab. Upload a PDF, then ask questions.
6. Check service health at `/health/ready` and `/health/live`.

The Blueprint configures one instance because the local FAISS index requires single-writer local storage. The attached persistent disk preserves uploads and the index across deploys, but prevents horizontal scaling and may affect availability during deploys. For multi-instance scale, migrate storage and vector search to managed/shared services. Render may charge for the selected instance and disk; review current pricing before applying.

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

## API

- `GET /health/live` — process liveness
- `GET /health/ready` — readiness
- `POST /api/upload` — multipart field `file`; default upload limit is 20 MiB
- `POST /api/chat` — JSON body `{"question":"..."}`

Protected API requests require `Authorization: Bearer <API_KEY>`.

## Configuration and operations

See `.env.example`. `MAX_UPLOAD_BYTES` controls the maximum accepted PDF size. `OPENAI_API_KEY` enables model-generated answers; without it, the API returns a relevant retrieved passage. Store secrets in Render's environment settings, not in source control.

This is a safer single-instance deployment baseline, not a fully managed production platform. Before handling sensitive or high-volume workloads, add per-user authentication/authorization, rate limiting, malware scanning, retention/deletion workflows, monitoring and alerting. Scanned PDFs require OCR, which is not included. Treat PDF content and model output as untrusted.
