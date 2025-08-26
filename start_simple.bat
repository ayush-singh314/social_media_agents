@echo off
echo Starting Content Ideation Agent Microservice (Simple Mode)...
echo.
echo This will start the server without the ASGI factory warning
echo.
echo Make sure you have:
echo 1. Python installed
echo 2. Dependencies installed (pip install -r requirements.txt)
echo 3. .env file configured with your API keys
echo.
echo Starting server on http://127.0.0.1:8000
echo.
echo Test URLs:
echo - Frontend: http://127.0.0.1:8000/static/
echo - Test Page: http://127.0.0.1:8000/static/test.html
echo - API Docs: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server using the module approach
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

pause
