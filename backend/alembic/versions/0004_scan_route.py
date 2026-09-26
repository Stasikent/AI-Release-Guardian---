"""add route identity to scans"""
from alembic import op
import sqlalchemy as sa

revision="0004_scan_route"
down_revision="0003_project_base_url"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("scans", sa.Column("route", sa.String(500), nullable=False, server_default="/"))
    op.create_index("ix_scans_route", "scans", ["route"])
    op.alter_column("scans", "route", server_default=None)

def downgrade():
    op.drop_index("ix_scans_route", table_name="scans")
    op.drop_column("scans", "route")
