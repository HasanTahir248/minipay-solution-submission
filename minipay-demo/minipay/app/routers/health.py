from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db import fetch_one

router = APIRouter()


@router.get("/health")
def health():
    try:
        fetch_one("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "error", "detail": str(e)})
