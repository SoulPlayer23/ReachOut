from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from crypto import decrypt, encrypt
from db import get_db
from models import GmailToken, User
from routers.auth import ALGORITHM, get_current_user
from schemas import GmailStatusOut

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

router = APIRouter(prefix="/gmail", tags=["gmail"])


def _gmail_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_gmail_redirect_uri],
            }
        },
        scopes=GMAIL_SCOPES,
        redirect_uri=settings.google_gmail_redirect_uri,
    )


_ALLOWED_RETURN_PATHS = {"/onboarding/connections", "/app/settings"}


def _create_gmail_state(user_id: int, return_to: str = "/onboarding/connections") -> str:
    if return_to not in _ALLOWED_RETURN_PATHS:
        return_to = "/onboarding/connections"
    expire = datetime.utcnow() + timedelta(minutes=10)
    return jwt.encode(
        {"exp": expire, "type": "gmail_state", "user_id": user_id, "return_to": return_to},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def _decode_gmail_state(state: str) -> tuple[int, str]:
    try:
        payload = jwt.decode(state, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "gmail_state":
            raise ValueError
        return_to = payload.get("return_to", "/onboarding/connections")
        if return_to not in _ALLOWED_RETURN_PATHS:
            return_to = "/onboarding/connections"
        return int(payload["user_id"]), return_to
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")


def get_valid_credentials(db: Session, user: User) -> Credentials:
    """Load Gmail credentials for a user, refreshing the access token if expired."""
    token_row = db.query(GmailToken).filter(GmailToken.user_id == user.id).first()
    if not token_row:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Gmail not connected")

    creds = Credentials(
        token=decrypt(token_row.access_token_enc),
        refresh_token=decrypt(token_row.refresh_token_enc),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=GMAIL_SCOPES,
    )
    creds.expiry = token_row.expiry

    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        token_row.access_token_enc = encrypt(creds.token)
        token_row.expiry = creds.expiry
        db.commit()

    return creds


@router.get("/connect")
def gmail_connect(
    return_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Return the Google OAuth URL for Gmail authorization."""
    flow = _gmail_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        state=_create_gmail_state(current_user.id, return_to or "/onboarding/connections"),
    )
    return {"url": auth_url}


@router.get("/callback")
def gmail_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """Google redirects here after the user grants Gmail access."""
    user_id, return_to = _decode_gmail_state(state)

    flow = _gmail_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    token_row = db.query(GmailToken).filter(GmailToken.user_id == user_id).first()
    if token_row:
        token_row.access_token_enc = encrypt(creds.token)
        token_row.refresh_token_enc = encrypt(creds.refresh_token)
        token_row.expiry = creds.expiry
    else:
        db.add(GmailToken(
            user_id=user_id,
            access_token_enc=encrypt(creds.token),
            refresh_token_enc=encrypt(creds.refresh_token),
            expiry=creds.expiry,
        ))
    db.commit()

    return RedirectResponse(f"{return_to}?gmail=connected")


@router.get("/status", response_model=GmailStatusOut)
def gmail_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token = db.query(GmailToken).filter(GmailToken.user_id == current_user.id).first()
    return GmailStatusOut(connected=token is not None)
