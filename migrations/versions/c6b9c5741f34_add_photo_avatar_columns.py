"""add photo/avatar columns

Revision ID: c6b9c5741f34
Revises: ce681593aaec
Create Date: 2026-06-12 11:03:18.218088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6b9c5741f34'
down_revision = 'ce681593aaec'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo', sa.String(length=255), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('avatar')

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_column('photo')
