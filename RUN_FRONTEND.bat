@echo off
REM Quick Frontend Runner for Windows

cd frontend
echo Installing dependencies...
call npm install -q 2>nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       🎨 Identity Spoofing Detection - Frontend Starting       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Dashboard: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm start
