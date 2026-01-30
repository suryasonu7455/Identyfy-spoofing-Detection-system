@echo off
REM Quick Backend Runner for Windows

cd backend
echo Installing dependencies...
pip install -q -r requirements.txt 2>nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       🚀 Identity Spoofing Detection - Backend Starting        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Listening on: http://localhost:5000
echo API Health: http://localhost:5000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
