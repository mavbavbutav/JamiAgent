from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db_session

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(session: Session = Depends(get_db_session)) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready"}


@router.get("/version")
def version() -> dict[str, str]:
    return {"version": "0.5.0"}
