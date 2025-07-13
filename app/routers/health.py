from fastapi import APIRouter, Depends
from app.schemas.response import BaseResponse
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/ping", response_model=BaseResponse)
async def ping():
    return BaseResponse.success_response(data={"message": "PONG"})