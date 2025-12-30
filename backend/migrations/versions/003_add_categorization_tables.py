"""Add categorization learning tables

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 10:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categorization_rules table for storing learned patterns
    op.create_table(
        'categorization_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pattern', sa.String(length=200), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('times_applied', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('times_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categorization_rules_pattern'), 'categorization_rules', ['pattern'], unique=False)
    op.create_index(op.f('ix_categorization_rules_category_id'), 'categorization_rules', ['category_id'], unique=False)
    
    # Create user_corrections table to track manual categorization changes
    op.create_table(
        'user_corrections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('old_category_id', sa.Integer(), nullable=True),
        sa.Column('new_category_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['old_category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['new_category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_corrections_transaction_id'), 'user_corrections', ['transaction_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_corrections_transaction_id'), table_name='user_corrections')
    op.drop_table('user_corrections')
    op.drop_index(op.f('ix_categorization_rules_category_id'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_pattern'), table_name='categorization_rules')
    op.drop_table('categorization_rules')
