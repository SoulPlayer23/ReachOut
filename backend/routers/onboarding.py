import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crypto import decrypt, encrypt
from db import get_db
from models import ApiKeys, Preferences, User
from routers.auth import get_current_user
from schemas import ApiKeysCreate, ApiKeysStatus, PreferencesCreate, PreferencesOut
from config import settings

router = APIRouter(tags=["onboarding"])


@router.get("/onboarding/resume-check")
def resume_check(current_user: User = Depends(get_current_user)):
    found = os.path.isfile(settings.resume_path)
    return {"found": found, "path": settings.resume_path}


@router.post("/preferences", response_model=PreferencesOut)
def save_preferences(
    body: PreferencesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prefs = db.query(Preferences).filter(Preferences.user_id == current_user.id).first()
    if prefs:
        prefs.default_location = body.default_location
        prefs.target_roles = body.target_roles
        prefs.tone = body.tone
        if body.resume_filename:
            prefs.resume_filename = body.resume_filename
    else:
        prefs = Preferences(user_id=current_user.id, **body.model_dump())
        db.add(prefs)
    db.commit()
    db.refresh(prefs)
    return prefs


@router.get("/preferences", response_model=PreferencesOut | None)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Preferences).filter(Preferences.user_id == current_user.id).first()


@router.post("/api-keys", response_model=ApiKeysStatus)
def save_api_keys(
    body: ApiKeysCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    keys = db.query(ApiKeys).filter(ApiKeys.user_id == current_user.id).first()
    if not keys:
        keys = ApiKeys(user_id=current_user.id)
        db.add(keys)

    if body.serper_key is not None:
        keys.serper_key_enc = encrypt(body.serper_key) if body.serper_key else None
    if body.hunter_key is not None:
        keys.hunter_key_enc = encrypt(body.hunter_key) if body.hunter_key else None
    if body.apollo_key is not None:
        keys.apollo_key_enc = encrypt(body.apollo_key) if body.apollo_key else None
    if body.snov_key is not None:
        keys.snov_key_enc = encrypt(body.snov_key) if body.snov_key else None
    if body.ollama_api_key is not None:
        keys.ollama_api_key_enc = encrypt(body.ollama_api_key) if body.ollama_api_key else None

    db.commit()
    db.refresh(keys)
    return _keys_status(keys)


@router.get("/api-keys/status", response_model=ApiKeysStatus)
def get_api_keys_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    keys = db.query(ApiKeys).filter(ApiKeys.user_id == current_user.id).first()
    if not keys:
        return ApiKeysStatus(serper=False, hunter=False, apollo=False, snov=False, ollama=False)
    return _keys_status(keys)


def _keys_status(keys: ApiKeys) -> ApiKeysStatus:
    return ApiKeysStatus(
        serper=bool(keys.serper_key_enc),
        hunter=bool(keys.hunter_key_enc),
        apollo=bool(keys.apollo_key_enc),
        snov=bool(keys.snov_key_enc),
        ollama=bool(keys.ollama_api_key_enc),
    )
