import os
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.sql import desc
import redis.asyncio as redis
from google.cloud import storage
import datetime

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
        self.db.expire_all()
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).order_by(desc(Task.created_at))

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return tasks

    async def get_task_by_id(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Get a single task by its ID and verify it belongs to the user
        """
        query = select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        )

        result = await self.db.execute(query)
        task = result.scalars().first()

        return task

    def generate_signed_url(self, gcs_uri: str, expiration: int = 3600) -> str:
        """
        Generate a signed URL for a GCS object

        Args:
            gcs_uri: The GCS URI in format 'gs://{bucket_name}/{object_name}'
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL string
        """
        if not gcs_uri or not gcs_uri.startswith('gs://'):
            return None

        # Parse bucket and object from URI
        # Format: gs://bucket-name/path/to/object
        parts = gcs_uri[5:].split('/', 1)  # Remove 'gs://' and split on first '/'
        if len(parts) != 2:
            return None

        bucket_name, object_name = parts

        # Create storage client and generate signed URL
        print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_name)

        # Generate signed URL with expiration time
        url = blob.generate_signed_url(
            version='v4',
            expiration=datetime.timedelta(seconds=expiration),
            method='GET'
        )

        return url
