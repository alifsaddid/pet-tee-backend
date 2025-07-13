from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar('T')


class ErrorModel(BaseModel):
    code: str
    message: str


class BaseResponse(GenericModel, Generic[T]):
    success: bool = True
    errors: Optional[List[ErrorModel]] = Field(default_factory=list)
    data: Optional[T] = None

    @classmethod
    def success_response(cls, data: Optional[T] = None) -> 'BaseResponse[T]':
        return cls(success=True, data=data)

    @classmethod
    def error_response(cls, errors: List[ErrorModel]) -> 'BaseResponse[T]':
        return cls(success=False, errors=errors)
