"""Visitor-owned saved meal plans. Existing shops and menus are preserved."""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('saved_plans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_hash', sa.String(64), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('budget', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_saved_plans_owner_hash', 'saved_plans', ['owner_hash'])
    op.create_table('saved_plan_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('saved_plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('shop_name', sa.String(100), nullable=False),
        sa.Column('location', sa.String(200), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False))
    op.create_index('ix_saved_plan_items_plan_id', 'saved_plan_items', ['plan_id'])
    if op.get_bind().dialect.name == 'postgresql':
        # All access is through the backend. No direct public Data API policies.
        op.execute('ALTER TABLE saved_plans ENABLE ROW LEVEL SECURITY')
        op.execute('ALTER TABLE saved_plan_items ENABLE ROW LEVEL SECURITY')


def downgrade():
    op.drop_table('saved_plan_items')
    op.drop_table('saved_plans')
