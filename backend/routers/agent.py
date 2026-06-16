from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from agent.orchestrator import run_stream
from db import get_db
from models import User
from routers.auth import get_current_user
from schemas import ChatMessage

router = APIRouter(tags=["agent"])


@router.post("/chat/stream")
def chat_stream(
    body: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return StreamingResponse(
        run_stream(body.message, current_user, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
