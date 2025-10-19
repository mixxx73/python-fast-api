"""add is_admin to users

Revision ID: 0004_add_is_admin
Revises: 0003_exp_tstz
Create Date: 2025-09-11
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_add_is_admin'
down_revision = '0003_exp_tstz'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'is_admin')