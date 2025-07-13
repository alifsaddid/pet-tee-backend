from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserResponseData, UserLogin
from app.schemas.response import BaseResponse, ErrorModel
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserResponseData)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = await AuthService.create_user(user_data, db)
    user_out = UserResponse.model_validate(user, from_attributes=True)
    return UserResponseData.success_response(data=user_out)


@router.post("/login", response_model=BaseResponse)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = await AuthService.authenticate_user(user_login.username, user_login.password, db)
    if not user:
        return BaseResponse.error_response(errors=[
            ErrorModel(code="INVALID_CREDENTIALS", message="Incorrect username or password")
        ])

    token_data = await AuthService.create_user_token(user)
    return BaseResponse.success_response(data=token_data)