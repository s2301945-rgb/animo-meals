"""Create related canteen tables."""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('stalls',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String(100), nullable=False, unique=True),
                    sa.Column('location', sa.String(200), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('menu_items',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('stall_id', sa.Integer, sa.ForeignKey('stalls.id'), nullable=False),
                    sa.Column('name', sa.String(120), nullable=False),
                    sa.Column('description', sa.Text, nullable=True),
                    sa.Column('price', sa.Numeric(10, 2), nullable=False),
                    sa.Column('category', sa.String(30), nullable=False),
                    sa.Column('is_available', sa.Boolean, nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
                    sa.CheckConstraint('price >= 0', name='price_nonnegative'))
    op.create_index('ix_menu_items_stall_id', 'menu_items', ['stall_id'])


def downgrade():
    op.drop_index('ix_menu_items_stall_id', table_name='menu_items')
    op.drop_table('menu_items')
    op.drop_table('stalls')
