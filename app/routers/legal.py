from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from functools import lru_cache

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
LEGAL_DIR = BASE_DIR / "legal_content"

@lru_cache()
def read_file(filename: str):
    if ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = LEGAL_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return file_path.read_text(encoding="utf-8")

@router.get("/terms", response_class=HTMLResponse)
def get_terms():
    return read_file("terms.html")

@router.get("/privacy", response_class=HTMLResponse)
def get_privacy():
    return read_file("privacy.html")