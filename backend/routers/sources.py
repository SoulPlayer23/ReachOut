from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import Source, User
from routers.auth import get_current_user
from schemas import SourceOut, SourceToggle

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceOut])
def list_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Source).filter(Source.user_id == current_user.id).all()


@router.patch("/sources/{source_key}", response_model=SourceOut)
def toggle_source(
    source_key: str,
    body: SourceToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source = (
        db.query(Source)
        .filter(Source.user_id == current_user.id, Source.source_key == source_key)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.enabled = body.enabled
    db.commit()
    db.refresh(source)
    return source
