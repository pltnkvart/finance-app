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
            {'name': 'Продукты', 'description': 'Покупка продуктов и товаров для дома'},
            {'name': 'Транспорт', 'description': 'Общественный транспорт, такси, топливо'},
            {'name': 'Кафе и рестораны', 'description': 'Кафе, рестораны, доставка еды'},
            {'name': 'Покупки', 'description': 'Одежда, электроника и другие покупки'},
            {'name': 'Развлечения', 'description': 'Кино, мероприятия, хобби'},
            {'name': 'Счета и подписки', 'description': 'Коммунальные услуги, подписки, регулярные платежи'},
            {'name': 'Здоровье', 'description': 'Медицина, аптеки, лечение'},
            {'name': 'Образование', 'description': 'Курсы, книги, обучение'},
            {'name': 'Путешествия', 'description': 'Поездки, отпуск, проживание'},
            {'name': 'Другое', 'description': 'Расходы без категории'},
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
