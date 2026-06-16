from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from models import OutreachLog, User
from routers.auth import get_current_user
from schemas import OutreachLogOut

router = APIRouter(tags=["history"])


@router.get("/history", response_model=list[OutreachLogOut])
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    return (
        db.query(OutreachLog)
        .filter(OutreachLog.user_id == current_user.id)
        .order_by(OutreachLog.sent_at.desc().nullslast(), OutreachLog.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
