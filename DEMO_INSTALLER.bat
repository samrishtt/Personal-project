@echo off
setlocal
title SynapseForge - One-Click Demo Installer

echo ==========================================================
echo    ⚡ SYNAPSEFORGE: COLLABORATIVE INTELLIGENCE DEMO ⚡
echo ==========================================================
echo.
echo This script will set up everything you need to run the demo.
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please download it from python.org
    pause
    exit /b
)

:: 2. Create Virtual Environment
echo [1/4] Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b
)

:: 3. Install Dependencies
echo [2/4] Installing research-grade dependencies (this may take a minute)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b
)

:: 4. Start the Server
echo.
echo [3/4] SUCCESS! Environment is ready.
echo [4/4] Starting SynapseForge Server...
echo.
echo ----------------------------------------------------------
echo  IMPORTANT: To see the "actually working" demo for FREE:
echo  1. Once the browser opens, look at the "Preset" dropdown.
echo  2. Select "Demo - Mock agents (free)".
echo  3. Type any query and hit "Launch Collaborative Synthesis".
echo ----------------------------------------------------------
echo.

start "" "http://127.0.0.1:5000"
python server.py

pause
