# Support Ticket Resolution Agent - Windows PowerShell Setup Script
# Run this script in PowerShell to set up and run the application

Write-Host "=== Support Ticket Resolution Agent Setup ===" -ForegroundColor Blue
Write-Host "Setting up the AI support agent with LangGraph workflow..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check if LangGraph CLI is installed
try {
    $langgraphVersion = langgraph version 2>&1
    Write-Host "Found LangGraph CLI: $langgraphVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing LangGraph CLI..." -ForegroundColor Yellow
    pip install langgraph-cli
}

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r project_requirements.txt

# Create necessary directories
Write-Host "Creating required directories..." -ForegroundColor Yellow
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
if (!(Test-Path "data")) { New-Item -ItemType Directory -Path "data" }
if (!(Test-Path "indexes")) { New-Item -ItemType Directory -Path "indexes" }

# Check for environment variables
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (!$env:GEMINI_API_KEY) {
    Write-Host "WARNING: GEMINI_API_KEY not set" -ForegroundColor Red
    Write-Host "Please set your Gemini API key:" -ForegroundColor Yellow
    Write-Host '$env:GEMINI_API_KEY = "your-api-key-here"' -ForegroundColor Cyan
}

# Display startup options
Write-Host ""
Write-Host "=== Startup Options ===" -ForegroundColor Blue
Write-Host "1. Streamlit Web Interface (Recommended)" -ForegroundColor Green
Write-Host "2. LangGraph CLI Development Mode" -ForegroundColor Green
Write-Host "3. Interactive Python Console" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Select startup mode (1-3)"

switch ($choice) {
    "1" {
        Write-Host "Starting Streamlit web interface..." -ForegroundColor Green
        Write-Host "Open your browser to: http://localhost:5000" -ForegroundColor Cyan
        streamlit run app.py --server.port 5000
    }
    "2" {
        Write-Host "Starting LangGraph development server..." -ForegroundColor Green
        Write-Host "LangGraph Studio will be available at: http://localhost:8123" -ForegroundColor Cyan
        langgraph dev
    }
    "3" {
        Write-Host "Starting interactive Python console..." -ForegroundColor Green
        python -i interactive_workflow.py
    }
    default {
        Write-Host "Invalid choice. Starting Streamlit by default..." -ForegroundColor Yellow
        streamlit run app.py --server.port 5000
    }
}

Write-Host "Setup complete! Press Ctrl+C to stop the application." -ForegroundColor Green