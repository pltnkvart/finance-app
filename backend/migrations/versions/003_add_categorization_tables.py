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
    # Create categorization_rules table
    op.create_table(
        'categorization_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pattern', sa.String(length=200), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('times_applied', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('times_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(
            ['category_id'],
            ['categories.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_categorization_rules_pattern'),
        'categorization_rules',
        ['pattern']
    )

    op.create_index(
        op.f('ix_categorization_rules_category_id'),
        'categorization_rules',
        ['category_id']
    )

    # Create user_corrections table
    op.create_table(
        'user_corrections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('old_category_id', sa.Integer(), nullable=True),
        sa.Column('new_category_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(
            ['transaction_id'],
            ['transactions.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['old_category_id'],
            ['categories.id'],
            ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['new_category_id'],
            ['categories.id'],
            ondelete='RESTRICT'
        ),

        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_user_corrections_transaction_id'),
        'user_corrections',
        ['transaction_id']
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_user_corrections_transaction_id'), table_name='user_corrections')
    op.drop_table('user_corrections')
    op.drop_index(op.f('ix_categorization_rules_category_id'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_pattern'), table_name='categorization_rules')
    op.drop_table('categorization_rules')
