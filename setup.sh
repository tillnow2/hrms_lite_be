#!/bin/bash

echo "================================================"
echo "HRMS Lite Backend - Quick Setup Script"
echo "================================================"
echo ""

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/4] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
else
    echo ".env file already exists"
fi

echo ""
echo "================================================"
echo "✅ Setup completed successfully!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MongoDB connection string"
echo "2. Make sure MongoDB is running"
echo "3. Run: uvicorn main:app --reload"
echo "4. Open: http://localhost:8000/docs"
echo ""
echo "Quick start command:"
echo "  uvicorn main:app --reload"
echo ""
