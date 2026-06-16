from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from google_auth_oauthlib.flow import Flow
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from db import get_db
from models import User
from schemas import GoogleVerifyRequest, TokenOut, UserOut
from seed import seed_sources

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

bearer_scheme = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["auth"])


def _google_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_auth_redirect_uri],
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.google_auth_redirect_uri,
    )


def _create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.secret_key, algorithm=ALGORITHM)


def _create_oauth_state() -> str:
    """Stateless CSRF token — signed JWT with 10-minute expiry."""
    expire = datetime.utcnow() + timedelta(minutes=10)
    return jwt.encode({"exp": expire, "type": "oauth_state"}, settings.secret_key, algorithm=ALGORITHM)


def _verify_oauth_state(state: str) -> bool:
    try:
        payload = jwt.decode(state, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("type") == "oauth_state"
    except JWTError:
        return False


def _find_or_create_user(db: Session, google_id: str, email: str, name: str, avatar_url: str | None) -> tuple[User, bool]:
    """Return (user, is_new). Shared by web callback and mobile verify."""
    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        return user, False

    # Also check by email in case the account predates Google login
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.google_id = google_id
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user, False

    user = User(google_id=google_id, email=email, name=name, avatar_url=avatar_url)
    db.add(user)
    db.commit()
    db.refresh(user)
    seed_sources(db, user.id)
    return user, True


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ── Web OAuth flow ────────────────────────────────────────────────────────────

@router.get("/google")
def google_login():
    """Redirect the browser to Google's OAuth consent screen."""
    flow = _google_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=_create_oauth_state(),
        prompt="select_account",
    )
    return RedirectResponse(auth_url)


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """Google redirects here after user grants consent."""
    if not _verify_oauth_state(state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

    flow = _google_flow()
    flow.fetch_token(code=code)

    idinfo = google_id_token.verify_oauth2_token(
        flow.credentials.id_token,
        google_requests.Request(),
        settings.google_client_id,
    )

    user, is_new = _find_or_create_user(
        db,
        google_id=idinfo["sub"],
        email=idinfo["email"],
        name=idinfo.get("name", idinfo["email"]),
        avatar_url=idinfo.get("picture"),
    )

    token = _create_token(user.id)
    next_path = "/onboarding/resume" if is_new else "/app/chat"
    return RedirectResponse(f"/auth/callback?token={token}&next={next_path}")


# ── Mobile token verification ─────────────────────────────────────────────────

@router.post("/google/verify", response_model=TokenOut)
def google_verify_mobile(body: GoogleVerifyRequest, db: Session = Depends(get_db)):
    """
    Mobile clients (Android/iOS) exchange a Google ID token obtained via the
    platform SDK for a ReachOut JWT. iOS apps using Sign in with Apple should
    hit a future /auth/apple/verify endpoint with the same shape.
    """
    try:
        idinfo = google_id_token.verify_oauth2_token(
            body.id_token,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token")

    user, _ = _find_or_create_user(
        db,
        google_id=idinfo["sub"],
        email=idinfo["email"],
        name=idinfo.get("name", idinfo["email"]),
        avatar_url=idinfo.get("picture"),
    )
    return TokenOut(access_token=_create_token(user.id))


# ── Shared ────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
