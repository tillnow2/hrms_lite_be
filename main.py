from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from app.config.database import connect_db, close_db
from app.routes import employee_routes, attendance_routes, dashboard_routes
from app.utils.exception_handlers import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.utils.logger import setup_logging

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting HRMS Lite API...")
    await connect_db()
    yield
    # Shutdown
    logger.info("Shutting down HRMS Lite API...")
    await close_db()

app = FastAPI(
    title="HRMS Lite API",
    description="Human Resource Management System - Lightweight Version",
    version="1.0.0",
    lifespan=lifespan
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "message": "HRMS Lite API is running",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "HRMS Lite Backend"}

# Include Routers
app.include_router(employee_routes.router, prefix="/api", tags=["Employees"])
app.include_router(attendance_routes.router, prefix="/api", tags=["Attendance"])
app.include_router(dashboard_routes.router, prefix="/api", tags=["Dashboard"])
