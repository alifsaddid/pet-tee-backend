from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.utils.auth import get_password_hash, verify_password, create_access_token


class AuthService:
    @staticmethod
    async def create_user(user_data: UserCreate, db: Session) -> User:
        # existing_user = db.query(User).filter(User.username == user_data.username).first()
        existing_user = await db.scalar(
            select(User)
            .where(User.username == user_data.username)
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            role=UserRole.USER
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def authenticate_user(username: str, password: str, db: Session):
        user = await db.scalar(
            select(User)
            .where(User.username == username)
        )
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def create_user_token(user: User):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "id": str(user.id)
            },
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
