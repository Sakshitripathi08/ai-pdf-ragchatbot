from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import APP_NAME, UPLOAD_DIR
from app.pdf_store import PDFRAGStore

app = FastAPI(title=APP_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")
store = PDFRAGStore()


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": APP_NAME}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    safe_name = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    chunk_count = store.index_pdf(file_path)
    return {
        "message": "PDF uploaded and indexed successfully.",
        "filename": safe_name,
        "chunks_indexed": chunk_count,
    }


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = store.ask(payload.question)
    return {"answer": answer}
