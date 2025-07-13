from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.sql import desc
import redis.asyncio as redis

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate
from app.services.redis_service import RedisService


class TaskService:
    def __init__(self, db: AsyncSession, redis_service: RedisService):
        self.db = db
        self.redis_service = redis_service

    async def create_task(self, task_data: TaskCreate, user_id: UUID) -> UUID:
        """
        Create a new task and push to Redis queue
        """
        # Create task in database
        new_task = Task(
            user_id=user_id,
            status=TaskStatus.CREATED,
            animal=task_data.animal,
            text=task_data.text
        )

        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)

        # Push task ID to Redis queue
        await self.redis_service.lpush(
            "generate_image_queue", 
            str(new_task.id)
        )

        return new_task.id

    async def get_user_tasks(self, user_id: UUID) -> List[Task]:
        """
        Get all tasks for a user
        """
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).order_by(desc(Task.created_at))

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return tasks
