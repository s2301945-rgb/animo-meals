"""Add quantities and catalog references while preserving saved price snapshots."""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('saved_plans', sa.Column('version', sa.Integer(), server_default='1', nullable=False))
    with op.batch_alter_table('saved_plan_items') as batch:
        batch.add_column(sa.Column('quantity', sa.Integer(), server_default='1', nullable=False))
        batch.add_column(sa.Column('menu_item_id', sa.Integer(), nullable=True))
        batch.create_foreign_key('fk_saved_item_menu', 'menu_items', ['menu_item_id'], ['id'], ondelete='SET NULL')
        batch.create_check_constraint('saved_item_quantity_range', 'quantity >= 1 AND quantity <= 20')


def downgrade():
    with op.batch_alter_table('saved_plan_items') as batch:
        batch.drop_constraint('fk_saved_item_menu', type_='foreignkey')
        batch.drop_constraint('saved_item_quantity_range', type_='check')
        batch.drop_column('menu_item_id')
        batch.drop_column('quantity')
    op.drop_column('saved_plans', 'version')
