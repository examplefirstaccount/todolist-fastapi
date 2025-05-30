from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PriorityLevel(Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_completed: bool = False
    priority: PriorityLevel = PriorityLevel.medium
    deadline: Optional[datetime] = None
    project_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    deadline: Optional[datetime] = None
    project_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
