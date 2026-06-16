"""google auth — replace password with google_id

Revision ID: a1c3e9f20d44
Revises: 3a9fb8dfb8a7
Create Date: 2026-06-16 00:01:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1c3e9f20d44"
down_revision: Union[str, None] = "3a9fb8dfb8a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove all existing rows — they have no google_id and can't be migrated
    op.execute("DELETE FROM sources")
    op.execute("DELETE FROM preferences")
    op.execute("DELETE FROM api_keys")
    op.execute("DELETE FROM gmail_tokens")
    op.execute("DELETE FROM outreach_log")
    op.execute("DELETE FROM users")

    op.drop_column("users", "hashed_password")
    op.add_column("users", sa.Column("google_id", sa.String(), nullable=False, server_default=""))
    op.add_column("users", sa.Column("avatar_url", sa.String(), nullable=True))
    # Remove the temporary server_default now that the column exists
    op.alter_column("users", "google_id", server_default=None)
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "google_id")
    op.add_column("users", sa.Column("hashed_password", sa.String(), nullable=False, server_default=""))
    op.alter_column("users", "hashed_password", server_default=None)
