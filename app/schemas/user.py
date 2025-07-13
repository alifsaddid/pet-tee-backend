from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid
from app.models.user import UserRole
from app.schemas.response import BaseResponse


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(UserBase):
    id: uuid.UUID
    hashed_password: str
    role: UserRole

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserResponseData(BaseResponse[UserResponse]):
    pass
