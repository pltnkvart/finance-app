"""Russify categories

Revision ID: 004
Revises: 003
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
    # Update category names to Russian
    op.execute("""
        UPDATE categories SET name = 'Продукты', description = 'Продукты и бакалея' WHERE name = 'Groceries';
        UPDATE categories SET name = 'Транспорт', description = 'Общественный транспорт, такси, топливо' WHERE name = 'Transportation';
        UPDATE categories SET name = 'Развлечения', description = 'Кино, концерты, хобби' WHERE name = 'Entertainment';
        UPDATE categories SET name = 'Коммунальные услуги', description = 'Электричество, вода, интернет, телефон' WHERE name = 'Utilities';
        UPDATE categories SET name = 'Рестораны', description = 'Кафе, рестораны, доставка еды' WHERE name = 'Restaurants';
        UPDATE categories SET name = 'Здоровье', description = 'Аптека, врачи, медицинские услуги' WHERE name = 'Healthcare';
        UPDATE categories SET name = 'Образование', description = 'Курсы, книги, обучение' WHERE name = 'Education';
        UPDATE categories SET name = 'Одежда', description = 'Одежда, обувь, аксессуары' WHERE name = 'Clothing';
        UPDATE categories SET name = 'Другое', description = 'Прочие расходы' WHERE name = 'Other';
    """)


def downgrade():
    # Revert to English
    op.execute("""
        UPDATE categories SET name = 'Groceries', description = 'Food and groceries' WHERE name = 'Продукты';
        UPDATE categories SET name = 'Transportation', description = 'Public transport, taxi, fuel' WHERE name = 'Транспорт';
        UPDATE categories SET name = 'Entertainment', description = 'Movies, concerts, hobbies' WHERE name = 'Развлечения';
        UPDATE categories SET name = 'Utilities', description = 'Electricity, water, internet, phone' WHERE name = 'Коммунальные услуги';
        UPDATE categories SET name = 'Restaurants', description = 'Cafes, restaurants, food delivery' WHERE name = 'Рестораны';
        UPDATE categories SET name = 'Healthcare', description = 'Pharmacy, doctors, medical services' WHERE name = 'Здоровье';
        UPDATE categories SET name = 'Education', description = 'Courses, books, training' WHERE name = 'Образование';
        UPDATE categories SET name = 'Clothing', description = 'Clothes, shoes, accessories' WHERE name = 'Одежда';
        UPDATE categories SET name = 'Other', description = 'Other expenses' WHERE name = 'Другое';
    """)
