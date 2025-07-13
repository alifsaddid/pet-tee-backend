from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.task import TaskStatus


class TaskBase(BaseModel):
    animal: str
    text: str

    @validator('text')
    def validate_text_length(cls, v):
        if len(v) > 8:
            raise ValueError('Text must be at most 8 characters')
        return v


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    status: TaskStatus

    class Config:
        orm_mode = True


class TaskCreateResponse(BaseModel):
    task_id: UUID


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]


class APIResponse(BaseModel):
    success: bool = True
    errors: List[str] = []
    data: Optional[dict] = None
