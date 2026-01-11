"""Add transaction type

Revision ID: 006
Revises: 005
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    transaction_type = sa.Enum('expense', 'income', name='transactiontype')
    transaction_type.create(op.get_bind(), checkfirst=True)

    op.add_column('transactions', sa.Column('transaction_type', transaction_type, nullable=False, server_default='expense'))
    op.create_index(op.f('ix_transactions_transaction_type'), 'transactions', ['transaction_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_transactions_transaction_type'), table_name='transactions')
    op.drop_column('transactions', 'transaction_type')

    transaction_type = sa.Enum('expense', 'income', name='transactiontype')
    transaction_type.drop(op.get_bind(), checkfirst=True)
