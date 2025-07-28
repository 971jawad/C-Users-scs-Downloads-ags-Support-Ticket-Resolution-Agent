@echo off
REM Support Ticket Resolution Agent - Windows Command Prompt Setup Script
REM Run this script in Command Prompt to set up and run the application

echo === Support Ticket Resolution Agent Setup ===
echo Setting up the AI support agent with LangGraph workflow...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Found Python installation

REM Check if LangGraph CLI is installed
langgraph version >nul 2>&1
if errorlevel 1 (
    echo Installing LangGraph CLI...
    pip install langgraph-cli
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r project_requirements.txt

REM Create necessary directories
echo Creating required directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "indexes" mkdir indexes

REM Check for environment variables
echo Checking environment configuration...
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY not set
    echo Please set your Gemini API key:
    echo set GEMINI_API_KEY=your-api-key-here
)

echo.
echo === Startup Options ===
echo 1. Streamlit Web Interface (Recommended)
echo 2. LangGraph CLI Development Mode
echo 3. Interactive Python Console
echo.

set /p choice="Select startup mode (1-3): "

if "%choice%"=="1" (
    echo Starting Streamlit web interface...
    echo Open your browser to: http://localhost:5000
    streamlit run app.py --server.port 5000
) else if "%choice%"=="2" (
    echo Starting LangGraph development server...
    echo LangGraph Studio will be available at: http://localhost:8123
    langgraph dev
) else if "%choice%"=="3" (
    echo Starting interactive Python console...
    python -i interactive_workflow.py
) else (
    echo Invalid choice. Starting Streamlit by default...
    streamlit run app.py --server.port 5000
)

echo Setup complete! Press Ctrl+C to stop the application.
pause