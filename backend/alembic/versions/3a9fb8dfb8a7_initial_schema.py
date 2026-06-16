"""initial schema

Revision ID: 3a9fb8dfb8a7
Revises:
Create Date: 2026-06-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "3a9fb8dfb8a7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("serper_key_enc", sa.Text(), nullable=True),
        sa.Column("hunter_key_enc", sa.Text(), nullable=True),
        sa.Column("apollo_key_enc", sa.Text(), nullable=True),
        sa.Column("snov_key_enc", sa.Text(), nullable=True),
        sa.Column("ollama_api_key_enc", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_api_keys_id", "api_keys", ["id"], unique=False)

    op.create_table(
        "gmail_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("access_token_enc", sa.Text(), nullable=False),
        sa.Column("refresh_token_enc", sa.Text(), nullable=False),
        sa.Column("expiry", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_gmail_tokens_id", "gmail_tokens", ["id"], unique=False)

    op.create_table(
        "outreach_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("recruiter_name", sa.String(), nullable=True),
        sa.Column("recruiter_email", sa.String(), nullable=False),
        sa.Column("email_subject", sa.String(), nullable=False),
        sa.Column("email_body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outreach_log_id", "outreach_log", ["id"], unique=False)

    op.create_table(
        "preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("default_location", sa.String(), nullable=True),
        sa.Column("target_roles", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("tone", sa.String(), nullable=False),
        sa.Column("resume_filename", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_preferences_id", "preferences", ["id"], unique=False)

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("source_key", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sources_id", "sources", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sources_id", table_name="sources")
    op.drop_table("sources")
    op.drop_index("ix_preferences_id", table_name="preferences")
    op.drop_table("preferences")
    op.drop_index("ix_outreach_log_id", table_name="outreach_log")
    op.drop_table("outreach_log")
    op.drop_index("ix_gmail_tokens_id", table_name="gmail_tokens")
    op.drop_table("gmail_tokens")
    op.drop_index("ix_api_keys_id", table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
