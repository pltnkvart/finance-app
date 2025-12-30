"""Seed default categories

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, String, Text, Integer

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a temporary table reference for bulk insert
    categories = table(
        'categories',
        column('name', String),
        column('description', Text)
    )
    
    # Insert default categories
    op.bulk_insert(
        categories,
        [
            {'name': 'Groceries', 'description': 'Food and household items'},
            {'name': 'Transport', 'description': 'Public transport, taxi, fuel'},
            {'name': 'Restaurants', 'description': 'Dining out, cafes, food delivery'},
            {'name': 'Shopping', 'description': 'Clothing, electronics, general shopping'},
            {'name': 'Entertainment', 'description': 'Movies, events, hobbies'},
            {'name': 'Bills', 'description': 'Utilities, subscriptions, regular payments'},
            {'name': 'Healthcare', 'description': 'Medical expenses, pharmacy'},
            {'name': 'Education', 'description': 'Courses, books, learning materials'},
            {'name': 'Travel', 'description': 'Vacation, trips, accommodation'},
            {'name': 'Other', 'description': 'Uncategorized expenses'},
        ]
    )


def downgrade() -> None:
    # Remove the seeded categories
    op.execute(
        """
        DELETE FROM categories 
        WHERE name IN (
            'Groceries', 'Transport', 'Restaurants', 'Shopping', 
            'Entertainment', 'Bills', 'Healthcare', 'Education', 
            'Travel', 'Other'
        )
        """
    )
