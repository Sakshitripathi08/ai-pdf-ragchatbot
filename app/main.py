from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.config import API_KEY, APP_NAME, MAX_UPLOAD_BYTES, UPLOAD_DIR
from app.pdf_store import PDFRAGStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)
store: PDFRAGStore | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global store
    store = PDFRAGStore()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.mount("/static", __import__("fastapi.staticfiles", fromlist=["StaticFiles"]).StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


async def require_api_key(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> None:
    if not API_KEY:
        return
    supplied = credentials.credentials if credentials else ""
    if not secrets.compare_digest(supplied, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token", headers={"WWW-Authenticate": "Bearer"})


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    if store is None:
        raise HTTPException(status_code=503, detail="Service is starting")
    return {"status": "ready"}


@app.post("/api/upload", dependencies=[Depends(require_api_key)])
async def upload_pdf(file: UploadFile = File(...)):
    file_path: Path | None = None
    try:
        if file.content_type not in ("application/pdf", "application/octet-stream"):
            raise HTTPException(status_code=415, detail="Upload must be a PDF")
        file_path = UPLOAD_DIR / f"{uuid4().hex}.pdf"
        size = 0
        with file_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="PDF exceeds the configured upload limit")
                destination.write(chunk)
        try:
            with fitz.open(file_path) as pdf:
                if pdf.is_encrypted or len(pdf) == 0:
                    raise HTTPException(status_code=422, detail="PDF is empty or password protected")
        except (fitz.FileDataError, fitz.MuPDFError) as exc:
            raise HTTPException(status_code=422, detail="Invalid PDF file") from exc
        if store is None:
            raise HTTPException(status_code=503, detail="Service is starting")
        chunks = store.index_pdf(file_path)
        if chunks == 0:
            raise HTTPException(status_code=422, detail="No extractable text found in PDF")
        return {"message": "PDF uploaded and indexed", "chunks_indexed": chunks}
    except HTTPException:
        if file_path and file_path.exists():
            file_path.unlink()
        raise
    except Exception:
        if file_path and file_path.exists():
            file_path.unlink()
        logger.exception("PDF upload/indexing failed")
        raise HTTPException(status_code=500, detail="PDF processing failed") from None
    finally:
        await file.close()


@app.post("/api/chat", dependencies=[Depends(require_api_key)])
def chat(payload: ChatRequest):
    if store is None:
        raise HTTPException(status_code=503, detail="Service is starting")
    try:
        return {"answer": store.ask(payload.question.strip())}
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=502, detail="Unable to generate an answer") from None
