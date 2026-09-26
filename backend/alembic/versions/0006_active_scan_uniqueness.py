"""enforce one active scan role per project route"""
from alembic import op

revision="0006_active_scan_uniqueness"
down_revision="0005_release_policy"
branch_labels=None
depends_on=None

def upgrade():
    # PostgreSQL partial unique index: history rows remain unlimited, while
    # baseline/current each have at most one active row per project + route.
    op.execute(
        "CREATE UNIQUE INDEX uq_scans_active_role_per_route "
        "ON scans (project_id, route, role) "
        "WHERE role IN ('baseline', 'current')"
    )

def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_scans_active_role_per_route")
