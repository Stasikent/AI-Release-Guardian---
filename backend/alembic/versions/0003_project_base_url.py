"""add project base url"""
from alembic import op
import sqlalchemy as sa

revision="0003_project_base_url"
down_revision="0002_knowledge"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("projects", sa.Column("base_url", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("projects", "base_url")
