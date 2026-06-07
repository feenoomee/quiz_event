"""Add created_at to users

Revision ID: 74699dbaea04
Revises: 8e06b80a54d5
Create Date: 2026-06-03 10:01:42.004036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74699dbaea04'
down_revision = '8e06b80a54d5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('created_at', sa.DateTime(), nullable=False,
                      server_default=sa.text("(datetime('now'))"))
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('created_at')
