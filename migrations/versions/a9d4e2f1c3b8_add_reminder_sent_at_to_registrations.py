"""Add reminder_sent_at to registrations

Revision ID: a9d4e2f1c3b8
Revises: bc8274cd5347
Create Date: 2026-08-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9d4e2f1c3b8'
down_revision = 'bc8274cd5347'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reminder_sent_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_column('reminder_sent_at')
