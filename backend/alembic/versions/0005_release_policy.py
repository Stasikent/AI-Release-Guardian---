"""add project release policy"""
from alembic import op
import sqlalchemy as sa

revision="0005_release_policy"
down_revision="0004_scan_route"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("projects", sa.Column("block_on", sa.String(20), nullable=False, server_default="CRITICAL"))
    op.add_column("projects", sa.Column("max_risk_score", sa.Integer(), nullable=False, server_default="100"))
    op.add_column("projects", sa.Column("require_all_routes", sa.Boolean(), nullable=False, server_default=sa.true()))

def downgrade():
    op.drop_column("projects", "require_all_routes")
    op.drop_column("projects", "max_risk_score")
    op.drop_column("projects", "block_on")
