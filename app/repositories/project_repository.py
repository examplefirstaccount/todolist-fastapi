from app.db.models import Project as DBProject
from app.repositories.base_repository import SQLAlchemyRepository


class ProjectRepository(SQLAlchemyRepository[DBProject]):
    """
    Repository class for Project database operations.
    """
    model = DBProject
