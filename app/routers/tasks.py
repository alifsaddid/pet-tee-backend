from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse, APIResponse, TaskCreateResponse
from app.services.task_service import TaskService
from app.core.db.session import get_db
from app.models.user import User
from app.core.services import TaskServiceDep
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/create", response_model=APIResponse)
async def create_task(
    task_data: TaskCreate,
    task_service: TaskServiceDep,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task and queue it for processing
    """
    task_id = await task_service.create_task(task_data, current_user.id)

    return APIResponse(
        success=True,
        data={
            "task_id": task_id
        }
    )


@router.get("", response_model=APIResponse)
async def get_tasks(
    task_service: TaskServiceDep,
    current_user: User = Depends(get_current_user),
):
    """
    Get all tasks for the current user
    """
    tasks = await task_service.get_user_tasks(current_user.id)

    return APIResponse(
        success=True,
        data={
            "tasks": [
                TaskResponse(
                    animal=task.animal,
                    text=task.text,
                    status=task.status
                ) for task in tasks
            ]
        }
    )
