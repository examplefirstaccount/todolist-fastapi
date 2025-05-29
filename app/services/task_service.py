from typing import Any, Dict, List, Optional

from app.api.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.utils.unitofwork import UnitOfWork


class TaskService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow


