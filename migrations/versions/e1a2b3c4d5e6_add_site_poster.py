"""add site_poster table for monthly afisha

Revision ID: e1a2b3c4d5e6
Revises: d72c9e83f4a1
Create Date: 2026-09-20 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e1a2b3c4d5e6"
down_revision = "d72c9e83f4a1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_poster",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("photo", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("site_poster")
