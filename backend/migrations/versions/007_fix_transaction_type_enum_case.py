"""Fix transaction type enum values

Revision ID: 007
Revises: 006
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE transactiontype_new AS ENUM ('expense', 'income')")
    op.execute("ALTER TABLE transactions ALTER COLUMN transaction_type DROP DEFAULT")
    op.execute(
        "ALTER TABLE transactions "
        "ALTER COLUMN transaction_type "
        "TYPE transactiontype_new "
        "USING lower(transaction_type::text)::transactiontype_new"
    )
    op.execute("DROP TYPE transactiontype")
    op.execute("ALTER TYPE transactiontype_new RENAME TO transactiontype")
    op.execute("ALTER TABLE transactions ALTER COLUMN transaction_type SET DEFAULT 'expense'")


def downgrade() -> None:
    op.execute("CREATE TYPE transactiontype_old AS ENUM ('EXPENSE', 'INCOME')")
    op.execute(
        "ALTER TABLE transactions "
        "ALTER COLUMN transaction_type "
        "TYPE transactiontype_old "
        "USING upper(transaction_type::text)::transactiontype_old"
    )
    op.execute("DROP TYPE transactiontype")
    op.execute("ALTER TYPE transactiontype_old RENAME TO transactiontype")
