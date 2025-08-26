@echo off
echo Starting Content Ideation Agent Microservice...
echo.
echo Make sure you have:
echo 1. Python installed
echo 2. Dependencies installed (pip install -r requirements.txt)
echo 3. .env file configured with your API keys
echo.
echo Starting server on http://localhost:8000
echo Frontend will be available at http://localhost:8000/static/
echo.
python server.py
pause
