from pydantic import BaseModel
from typing import Optional, Any

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: Optional[Any] = None
