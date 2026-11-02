# AI PDF RAG Chatbot

A lightweight Python starter for uploading PDF documents and chatting with them using retrieval-augmented generation (RAG).

Features:
- Upload one or more PDFs
- Extract and chunk text from PDF files
- Generate embeddings with `sentence-transformers`
- Search relevant passages with FAISS
- Answer questions with an LLM (OpenAI-compatible API when configured)
- Simple web UI for uploading and chatting

## Tech stack
- FastAPI
- Python
- PyMuPDF
- FAISS
- SentenceTransformers
- OpenAI SDK (optional for LLM answers)

## Quick start

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

4. Add your OpenAI API key in `.env` if you want real model answers.

5. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Open the app in your browser:
   ```text
   http://localhost:8000
   ```

## API endpoints

- `GET /api/health` — health check
- `POST /api/upload` — upload a PDF and index it
- `POST /api/chat` — ask a question based on indexed PDFs

## Environment variables

See `.env.example` for configuration options.

## Notes

This is a starter project intended for local development and experimentation. It is not a production-ready deployment template.
