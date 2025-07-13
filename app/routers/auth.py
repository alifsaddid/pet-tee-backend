from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserResponseData, UserLogin
from app.schemas.response import BaseResponse, ErrorModel
from app.services.auth_service import AuthService
from app.core.services import AuthServiceDep

router = APIRouter()

@router.post("/register", response_model=UserResponseData)
async def register(user_data: UserCreate, auth_service: AuthServiceDep):
    user = await auth_service.create_user(user_data)
    user_out = UserResponse.model_validate(user, from_attributes=True)
    return UserResponseData.success_response(data=user_out)


@router.post("/login", response_model=BaseResponse)
async def login(user_login: UserLogin, auth_service: AuthServiceDep):
    user = await auth_service.authenticate_user(user_login.username, user_login.password)
    if not user:
        return BaseResponse.error_response(errors=[
            ErrorModel(code="INVALID_CREDENTIALS", message="Incorrect username or password")
        ])

    token_data = await auth_service.create_user_token(user)
    return BaseResponse.success_response(data=token_data)