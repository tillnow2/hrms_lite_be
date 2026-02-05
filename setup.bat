@echo off
echo ================================================
echo HRMS Lite Backend - Quick Setup Script
echo ================================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
) else (
    echo .env file already exists
)

echo.
echo ================================================
echo ✅ Setup completed successfully!
echo ================================================
echo.
echo Next steps:
echo 1. Edit .env file with your MongoDB connection string
echo 2. Make sure MongoDB is running
echo 3. Run: uvicorn main:app --reload
echo 4. Open: http://localhost:8000/docs
echo.
echo Quick start command:
echo   uvicorn main:app --reload
echo.
pause
