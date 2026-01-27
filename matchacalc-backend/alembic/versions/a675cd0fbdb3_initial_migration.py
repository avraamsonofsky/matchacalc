"""Initial migration

Revision ID: a675cd0fbdb3
Revises: 
Create Date: 2026-01-22 18:39:03.108020

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a675cd0fbdb3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаём enum тип, если его нет
    propertyclass_enum = postgresql.ENUM('A_PRIME', 'A', 'B_PLUS', 'B', name='propertyclass', create_type=False)
    propertyclass_enum.create(op.get_bind(), checkfirst=True)
    
    # Добавляем колонку created_at в market_report_values, если её нет
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Проверяем существование таблицы перед проверкой колонок
    if inspector.has_table('market_report_values'):
        columns = [col['name'] for col in inspector.get_columns('market_report_values')]
        if 'created_at' not in columns:
            op.add_column('market_report_values', 
                         sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    
    # Добавляем колонку created_at в scenario_configs, если её нет
    if inspector.has_table('scenario_configs'):
        columns = [col['name'] for col in inspector.get_columns('scenario_configs')]
        if 'created_at' not in columns:
            op.add_column('scenario_configs', 
                         sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    
    # Добавляем колонку created_at в subscriptions, если её нет
    if inspector.has_table('subscriptions'):
        columns = [col['name'] for col in inspector.get_columns('subscriptions')]
        if 'created_at' not in columns:
            op.add_column('subscriptions', 
                         sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    # Удаляем колонки при откате
    op.drop_column('subscriptions', 'created_at')
    op.drop_column('scenario_configs', 'created_at')
    op.drop_column('market_report_values', 'created_at')
