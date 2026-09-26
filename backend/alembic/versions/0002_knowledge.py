"""add project knowledge base"""
from alembic import op
import sqlalchemy as sa
revision="0002_knowledge"
down_revision="0001_projects_scans"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("knowledge_documents",
      sa.Column("id",sa.Integer(),primary_key=True),
      sa.Column("project_id",sa.Integer(),sa.ForeignKey("projects.id",ondelete="CASCADE"),nullable=False),
      sa.Column("title",sa.String(200),nullable=False),
      sa.Column("source",sa.String(500),nullable=False),
      sa.Column("content",sa.Text(),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_knowledge_documents_project_id","knowledge_documents",["project_id"])
def downgrade():
    op.drop_table("knowledge_documents")
