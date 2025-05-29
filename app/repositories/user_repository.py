from app.db.models import User as DBUser
from app.repositories.base_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[DBUser]):
    """
    Repository class for User database operations.
    """
    model = DBUser
