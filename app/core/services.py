from fastapi import Depends
from typing import Annotated

from app.core.db.session import get_db
from app.core.redis import get_redis
from app.services.task_service import TaskService
from app.services.redis_service import RedisService
from app.services.auth_service import AuthService


def get_redis_service(redis=Depends(get_redis)):
    return RedisService(redis)


def get_task_service(redis_service: RedisService = Depends(get_redis_service), db=Depends(get_db)):
    return TaskService(db, redis_service)


def get_auth_service(db=Depends(get_db)):
    return AuthService(db)


# Type annotations for cleaner dependency injection
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
RedisServiceDep = Annotated[RedisService, Depends(get_redis_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
