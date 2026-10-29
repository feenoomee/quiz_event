"""Add the site-wide player chat.

Revision ID: b7c8d9e0f1a2
Revises: e1a2b3c4d5e6
"""
from alembic import op
import sqlalchemy as sa

revision = "b7c8d9e0f1a2"
down_revision = "e1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=2000), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"])


def downgrade():
    op.drop_index("ix_chat_messages_user_id", table_name="chat_messages")
    op.drop_table("chat_messages")
