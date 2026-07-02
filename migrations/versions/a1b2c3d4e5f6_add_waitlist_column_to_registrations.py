"""add waitlist column to registrations

Revision ID: a1b2c3d4e5f6
Revises: 3891c7b31257
Create Date: 2026-07-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '3891c7b31257'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('waitlist', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade():
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_column('waitlist')
