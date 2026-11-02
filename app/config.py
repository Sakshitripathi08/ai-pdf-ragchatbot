from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
VECTOR_STORE_DIR = Path(os.getenv("VECTOR_STORE_DIR", "vector_store"))

UPLOAD_DIR = BASE_DIR / UPLOAD_DIR
VECTOR_STORE_DIR = BASE_DIR / VECTOR_STORE_DIR

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = os.getenv("APP_NAME", "AI PDF RAG Chatbot")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
