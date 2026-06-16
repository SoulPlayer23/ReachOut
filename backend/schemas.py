from datetime import datetime

from pydantic import BaseModel, EmailStr


# --- User ---

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleVerifyRequest(BaseModel):
    id_token: str


# --- Preferences ---

class PreferencesCreate(BaseModel):
    default_location: str | None = None
    target_roles: list[str] | None = None
    tone: str = "professional"
    resume_filename: str | None = None


class PreferencesOut(PreferencesCreate):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


# --- API Keys ---

class ApiKeysCreate(BaseModel):
    serper_key: str | None = None
    hunter_key: str | None = None
    apollo_key: str | None = None
    snov_key: str | None = None
    ollama_api_key: str | None = None


class ApiKeysStatus(BaseModel):
    serper: bool
    hunter: bool
    apollo: bool
    snov: bool
    ollama: bool


# --- Gmail ---

class GmailStatusOut(BaseModel):
    connected: bool


# --- Sources ---

class SourceOut(BaseModel):
    id: int
    source_key: str
    label: str
    category: str
    enabled: bool
    is_custom: bool

    model_config = {"from_attributes": True}


class SourceToggle(BaseModel):
    enabled: bool


# --- Outreach Log ---

class OutreachLogOut(BaseModel):
    id: int
    company: str
    role: str
    recruiter_name: str | None
    recruiter_email: str
    email_subject: str
    email_body: str
    status: str
    sent_at: datetime | None

    model_config = {"from_attributes": True}


# --- Chat ---

class ChatMessage(BaseModel):
    message: str
