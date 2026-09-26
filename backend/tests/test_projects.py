from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.project import ProjectCreate
from app.services.projects import create_project, get_project, list_projects

def test_project_crud() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        created = create_project(db, ProjectCreate(name="Demo", description="Test"))
        assert created.id is not None
        assert get_project(db, created.id).name == "Demo"
        assert len(list_projects(db)) == 1
