"""Add accounts and deposits tables

Revision ID: 005
Revises: 004
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('account_type', sa.Enum('CHECKING', 'SAVINGS', 'CREDIT_CARD', 'CASH', 'INVESTMENT', name='accounttype'), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('balance', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    
    # Create deposits table
    op.create_table(
        'deposits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'CANCELLED', name='depositstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], )
    )
    op.create_index(op.f('ix_deposits_id'), 'deposits', ['id'], unique=False)
    op.create_index(op.f('ix_deposits_account_id'), 'deposits', ['account_id'], unique=False)
    
    # Add account_id to transactions table
    op.add_column('transactions', sa.Column('account_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_transactions_account_id', 'transactions', 'accounts', ['account_id'], ['id'])
    
    # Create default cash account
    op.execute("""
        INSERT INTO accounts (name, description, account_type, currency, balance)
        VALUES ('Наличные', 'Основной счет для наличных денег', 'CASH', 'RUB', 0.00);
    """)


def downgrade():
    op.drop_constraint('fk_transactions_account_id', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'account_id')
    op.drop_index(op.f('ix_deposits_account_id'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_id'), table_name='deposits')
    op.drop_table('deposits')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
