"""Add first_name and second_name to users

Revision ID: 8e06b80a54d5
Revises: 810af9ec094a
Create Date: 2026-06-03 09:48:43.791940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e06b80a54d5'
down_revision = '810af9ec094a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=120), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('second_name', sa.String(length=120), nullable=False, server_default=''))

    op.execute("UPDATE users SET first_name = name, second_name = ''")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('first_name', server_default=None)
        batch_op.alter_column('second_name', server_default=None)
        batch_op.drop_column('name')


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=120), nullable=False, server_default=''))

    op.execute("UPDATE users SET name = first_name")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('name', server_default=None)
        batch_op.drop_column('second_name')
        batch_op.drop_column('first_name')
