"""init

Revision ID: 001
Revises: 
Create Date: 2026-02-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('total_conversions', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)

    op.create_table(
        'conversion_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('original_filename', sa.String(length=500), nullable=False),
        sa.Column('original_size_mb', sa.Float(), nullable=False),
        sa.Column('converted_size_mb', sa.Float(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversion_logs_telegram_id'), 'conversion_logs', ['telegram_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_conversion_logs_telegram_id'), table_name='conversion_logs')
    op.drop_table('conversion_logs')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')
