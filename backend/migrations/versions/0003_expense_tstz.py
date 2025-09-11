"""Make expenses.created_at timezone-aware (timestamptz)

Revision ID: 0003_exp_tstz
Revises: 0002_add_password
Create Date: 2025-09-11
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_exp_tstz'
down_revision = '0002_add_password'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ''
    if dialect == 'postgresql':
        # Convert naive timestamp to timestamptz, treating existing values as UTC
        op.execute("ALTER TABLE expenses ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")
        # Ensure server default generates current timestamp (timezone-aware)
        op.execute("ALTER TABLE expenses ALTER COLUMN created_at SET DEFAULT now()")
    else:
        # SQLite and others: no-op, column affinity is dynamic and app sets value
        pass


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ''
    if dialect == 'postgresql':
        # Remove server default and convert back to naive timestamp
        op.execute("ALTER TABLE expenses ALTER COLUMN created_at DROP DEFAULT")
        op.execute("ALTER TABLE expenses ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    else:
        pass
