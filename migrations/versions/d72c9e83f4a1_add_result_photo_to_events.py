"""add result photo to events

Revision ID: d72c9e83f4a1
Revises: a9d4e2f1c3b8
Create Date: 2026-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d72c9e83f4a1"
down_revision = "a9d4e2f1c3b8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("events", schema=None) as batch_op:
        batch_op.add_column(sa.Column("result_photo", sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table("events", schema=None) as batch_op:
        batch_op.drop_column("result_photo")
