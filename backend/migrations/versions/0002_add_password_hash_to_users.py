"""add password_hash to users

Revision ID: 0002_add_password
Revises: 0001_create_core
Create Date: 2025-09-11 00:05:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_password'
down_revision = '0001_create_core'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'password_hash')

