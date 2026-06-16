from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    google_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    preferences: Mapped["Preferences"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    api_keys: Mapped["ApiKeys"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    gmail_token: Mapped["GmailToken"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    sources: Mapped[list["Source"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    outreach_logs: Mapped[list["OutreachLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Preferences(Base):
    __tablename__ = "preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    default_location: Mapped[str | None] = mapped_column(String)
    target_roles: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    tone: Mapped[str] = mapped_column(String, default="professional")
    resume_filename: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="preferences")


class ApiKeys(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    serper_key_enc: Mapped[str | None] = mapped_column(Text)
    hunter_key_enc: Mapped[str | None] = mapped_column(Text)
    apollo_key_enc: Mapped[str | None] = mapped_column(Text)
    snov_key_enc: Mapped[str | None] = mapped_column(Text)
    ollama_api_key_enc: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="api_keys")


class GmailToken(Base):
    __tablename__ = "gmail_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    expiry: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="gmail_token")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    source_key: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)  # "job_board" | "recruiter"
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="sources")


class OutreachLog(Base):
    __tablename__ = "outreach_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    recruiter_name: Mapped[str | None] = mapped_column(String)
    recruiter_email: Mapped[str] = mapped_column(String, nullable=False)
    email_subject: Mapped[str] = mapped_column(String, nullable=False)
    email_body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)  # "pending" | "sent" | "failed"
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="outreach_logs")
