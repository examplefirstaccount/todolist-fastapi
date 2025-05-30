from typing import Any, Dict, List, Optional

from app.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.utils.unitofwork import UnitOfWork


class ProjectService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow


