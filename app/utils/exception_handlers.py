from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"][1:])  # Skip 'body'
        message = error["msg"]
        errors.append({
            "field": field,
            "message": message,
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
   
    logger.error(f"HTTP {exc.status_code} error on {request.url.path}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "errors": None
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    
    logger.exception(f"Unexpected error on {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "errors": None
        }
    )
