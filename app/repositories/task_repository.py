from app.db.models import Task as DBTask
from app.repositories.base_repository import SQLAlchemyRepository


class TaskRepository(SQLAlchemyRepository[DBTask]):
    """
    Repository class for Task database operations.
    """
    model = DBTask
