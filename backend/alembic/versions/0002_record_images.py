"""Optional photos for shops and menu items; existing rows remain unchanged."""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stalls', sa.Column('image_url', sa.String(2048), nullable=True))
    op.add_column('menu_items', sa.Column('image_url', sa.String(2048), nullable=True))


def downgrade():
    op.drop_column('menu_items', 'image_url')
    op.drop_column('stalls', 'image_url')
