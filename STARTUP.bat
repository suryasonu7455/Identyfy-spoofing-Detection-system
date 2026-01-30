@echo off
REM Identity Spoofing Detection System - Windows Quick Start

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║   🔐 Identity Spoofing Detection System - Windows Startup      ║
echo ║   Problem: Prevent identity spoofing in gated communities     ║
echo ║   Status: READY TO DEMO ✅                                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo 📁 Project Structure:
echo.
echo identity-spoofing-detection/
echo ├── backend/            (Flask API)
echo ├── frontend/           (React Dashboard)
echo ├── Dockerfile
echo ├── docker-compose.yml
echo ├── README.md
echo ├── PRESENTATION.md
echo ├── DEMO_SCRIPT.md
echo └── QUICKSTART.sh
echo.

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ QUICK START OPTIONS                                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo [1] Setup Backend (Python + Dependencies)
echo [2] Setup Frontend (Node.js + npm)
echo [3] Run Both (Backend + Frontend)
echo [4] Run with Docker (docker-compose)
echo [5] Test API Endpoints
echo [6] View Documentation
echo [X] Exit
echo.

set /p choice="Enter your choice (1-6 or X): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
if "%choice%"=="4" goto docker
if "%choice%"=="5" goto test
if "%choice%"=="6" goto docs
if /i "%choice%"=="X" goto exit
echo Invalid choice. Please try again.
goto start

:backend
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ BACKEND SETUP                                                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd backend

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error: Python not found. Please install Python 3.10+
    goto exit
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies (this may take 2-3 minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error installing packages
    goto exit
)

echo.
echo ✅ Backend setup complete!
echo.
echo To run the backend:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python app.py
echo   3. Backend will be at http://localhost:5000
echo.
pause
goto end

:frontend
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FRONTEND SETUP                                                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd frontend

echo Checking for Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js not found
    echo Please install Node.js from https://nodejs.org/
    goto exit
)

echo.
echo Installing npm dependencies (this may take 2-3 minutes)...
call npm install
if errorlevel 1 (
    echo ❌ Error installing npm packages
    goto exit
)

echo.
echo ✅ Frontend setup complete!
echo.
echo To run the frontend:
echo   1. Run: npm start
echo   2. Dashboard will be at http://localhost:3000
echo.
pause
goto end

:both
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ SETUP BOTH BACKEND AND FRONTEND                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Step 1: Setting up backend...
echo ────────────────────────────────
cd backend
python -m venv venv
call venv\Scripts\activate.bat
echo Installing backend dependencies...
pip install -r requirements.txt
cd ..

echo.
echo Step 2: Setting up frontend...
echo ────────────────────────────────
cd frontend
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js not found. Please install from https://nodejs.org/
    cd ..
    goto exit
)
echo Installing frontend dependencies...
call npm install
cd ..

echo.
echo ✅ Setup complete!
echo.
echo IMPORTANT: You need TWO separate terminals
echo.
echo Terminal 1 - Run Backend:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo Terminal 2 - Run Frontend:
echo   cd frontend
echo   npm start
echo.
echo Then open:
echo   Dashboard: http://localhost:3000
echo   API: http://localhost:5000
echo.
pause
goto end

:docker
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ DOCKER DEPLOYMENT                                               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker not installed
    echo Please install Docker Desktop from https://www.docker.com/
    goto exit
)

echo Starting Docker containers...
docker-compose up -d

echo.
echo ⏳ Waiting for containers to start...
timeout /t 10 /nobreak

echo.
echo ✅ Docker deployment complete!
echo.
echo Services running on:
echo   Backend:   http://localhost:5000
echo   Frontend:  http://localhost:3000
echo   Database:  PostgreSQL on port 5432
echo.
echo View logs: docker-compose logs -f
echo Stop services: docker-compose down
echo.
pause
goto end

:test
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ API ENDPOINT TESTS                                              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Testing API health...
curl http://localhost:5000/api/health
if errorlevel 1 (
    echo ❌ Backend not running. Start it first with:
    echo   cd backend
    echo   python app.py
    goto exit
)

echo.
echo ✅ API is healthy!
echo.
echo Other endpoints you can test:
echo.
echo 1. Register user:
echo   curl -X POST http://localhost:5000/api/auth/register-user ^
echo     -H "Content-Type: application/json" ^
echo     -d "{\"name\":\"John Doe\",\"email\":\"john@example.com\",\"phone\":\"9876543210\",\"unit\":\"A101\"}"
echo.
echo 2. Get dashboard overview:
echo   curl http://localhost:5000/api/dashboard/overview
echo.
echo 3. Get access logs:
echo   curl http://localhost:5000/api/access/all-access-logs
echo.
pause
goto end

:docs
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ DOCUMENTATION                                                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Available documentation files:
echo.
echo 📖 README.md
echo    • Complete system documentation
echo    • Feature explanations
echo    • API endpoint reference
echo    • Deployment instructions
echo.
echo 🎬 DEMO_SCRIPT.md
echo    • Live demo walkthrough (12 minutes)
echo    • Step-by-step instructions
echo    • Expected outputs
echo    • Q&A answers for judges
echo.
echo 🎯 PRESENTATION.md
echo    • 18-slide presentation
echo    • Speaker notes for each slide
echo    • Competitive analysis
echo    • Market positioning
echo.
echo 📋 PROJECT_SUMMARY.md
echo    • What you've accomplished
echo    • Project structure
echo    • Key metrics
echo    • Winning strategy
echo.
echo ⚡ QUICKSTART.sh
echo    • Bash version of quick start
echo    • For Mac/Linux users
echo.
echo.
echo Opening README.md...
start README.md
goto end

:exit
echo.
echo Goodbye! Good luck with the hackathon! 🏆
echo.
pause
goto end

:end
endlocal
exit /b 0
