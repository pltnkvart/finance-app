"""Add parent category support

Revision ID: 005
Revises: 004
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'], unique=False)
    op.create_foreign_key(
        'fk_categories_parent_id',
        'categories',
        'categories',
        ['parent_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_categories_parent_id', 'categories', type_='foreignkey')
    op.drop_index(op.f('ix_categories_parent_id'), table_name='categories')
    op.drop_column('categories', 'parent_id')
