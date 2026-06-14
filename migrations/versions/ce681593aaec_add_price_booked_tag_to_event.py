"""Add price, booked, tag to Event

Revision ID: ce681593aaec
Revises: 74699dbaea04
Create Date: 2026-06-12 00:48:49.222453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce681593aaec'
down_revision = '74699dbaea04'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('booked', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('tag', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_column('tag')
        batch_op.drop_column('booked')
        batch_op.drop_column('price')
