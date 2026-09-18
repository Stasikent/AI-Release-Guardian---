"""initial projects and scans tables"""
from alembic import op
import sqlalchemy as sa
revision="0001_projects_scans"
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("projects",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("name",sa.String(120),nullable=False),sa.Column("description",sa.Text(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_projects_name","projects",["name"],unique=True)
    op.create_table("scans",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("project_id",sa.Integer(),sa.ForeignKey("projects.id",ondelete="CASCADE"),nullable=False),sa.Column("url",sa.Text(),nullable=False),sa.Column("title",sa.Text(),nullable=False),sa.Column("role",sa.String(20),nullable=False),sa.Column("total_testable_objects",sa.Integer(),nullable=False),sa.Column("payload_json",sa.Text(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_scans_project_id","scans",["project_id"])
    op.create_index("ix_scans_role","scans",["role"])
def downgrade():
    op.drop_table("scans")
    op.drop_table("projects")
