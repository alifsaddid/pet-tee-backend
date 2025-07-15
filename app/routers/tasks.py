import asyncio
import json
from uuid import UUID

from asyncpg.pgproto.pgproto import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.task import TaskCreate, APIResponse
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


@router.get(
    "",
    response_class=StreamingResponse,
    summary="Stream task list via SSE",
    description="""
    This endpoint uses **Server-Sent Events (SSE)** to stream the user's task list.

    - Returns `data: {json}` every 5 second.
    - Media type: `text/event-stream`.
    - Recommended to test with curl or EventSource in browser.
    - Swagger UI does not support live SSE output.
    """
)
async def get_tasks(
    task_service: TaskServiceDep,
    current_user: User = Depends(get_current_user),
):
    async def event_stream():
        while True:
            tasks = await task_service.get_user_tasks(current_user.id)

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.id),
                    "animal": task.animal,
                    "text": task.text,
                    "status": task.status,
                    "image_uri": None,
                })

            response_data = {
                "success": True,
                "data": {
                    "tasks": task_list
                }
            }

            yield f"data: {json.dumps(response_data)}\n\n"
            await asyncio.sleep(5)  # Wait 5 second before re-fetching

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


@router.get("/{id}", response_model=APIResponse)
async def get_task_by_id(
    id: UUID,
    task_service: TaskServiceDep,
    current_user: User = Depends(get_current_user)
):
    """
    Get a single task by ID with a signed URL for the image
    """
    # Get the task and verify ownership
    task = await task_service.get_task_by_id(id, current_user.id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Generate signed URL for image if available
    image_url = None
    if task.image_uri:
        image_url = task_service.generate_signed_url(task.image_uri)

    return APIResponse(
        success=True,
        data={
            "task_id": str(task.id),
            "animal": task.animal,
            "text": task.text,
            "image_url": image_url
        }
    )

