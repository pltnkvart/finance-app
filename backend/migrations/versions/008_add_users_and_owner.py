"""Add users and ownership columns

Revision ID: 008
Revises: 007
Create Date: 2026-01-08
"""
from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("telegram_user_id", sa.String(length=32), nullable=True),
        sa.Column("telegram_username", sa.String(length=64), nullable=True),
        sa.Column("telegram_link_code", sa.String(length=32), nullable=True),
        sa.Column("telegram_link_code_expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"], unique=True)
    op.create_index("ix_users_telegram_link_code", "users", ["telegram_link_code"], unique=False)

    op.add_column("accounts", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_foreign_key("fk_accounts_user_id_users", "accounts", "users", ["user_id"], ["id"])

    op.add_column("transactions", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_foreign_key("fk_transactions_user_id_users", "transactions", "users", ["user_id"], ["id"])

    op.add_column("deposits", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_deposits_user_id", "deposits", ["user_id"])
    op.create_foreign_key("fk_deposits_user_id_users", "deposits", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_deposits_user_id_users", "deposits", type_="foreignkey")
    op.drop_index("ix_deposits_user_id", table_name="deposits")
    op.drop_column("deposits", "user_id")

    op.drop_constraint("fk_transactions_user_id_users", "transactions", type_="foreignkey")
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_column("transactions", "user_id")

    op.drop_constraint("fk_accounts_user_id_users", "accounts", type_="foreignkey")
    op.drop_index("ix_accounts_user_id", table_name="accounts")
    op.drop_column("accounts", "user_id")

    op.drop_index("ix_users_telegram_link_code", table_name="users")
    op.drop_index("ix_users_telegram_user_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
