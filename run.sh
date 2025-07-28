#!/bin/bash
# Support Ticket Resolution Agent - Unix/Linux Setup Script
# Run this script to set up and run the application

echo "=== Support Ticket Resolution Agent Setup ==="
echo "Setting up the AI support agent with LangGraph workflow..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

echo "Found Python: $(python3 --version)"

# Check if LangGraph CLI is installed
if ! command -v langgraph &> /dev/null; then
    echo "Installing LangGraph CLI..."
    pip3 install langgraph-cli
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r project_requirements.txt

# Create necessary directories
echo "Creating required directories..."
mkdir -p logs data indexes

# Check for environment variables
echo "Checking environment configuration..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "WARNING: GEMINI_API_KEY not set"
    echo "Please set your Gemini API key:"
    echo "export GEMINI_API_KEY=\"your-api-key-here\""
fi

echo ""
echo "=== Startup Options ==="
echo "1. Streamlit Web Interface (Recommended)"
echo "2. LangGraph CLI Development Mode"
echo "3. Interactive Python Console"
echo ""

read -p "Select startup mode (1-3): " choice

case $choice in
    1)
        echo "Starting Streamlit web interface..."
        echo "Open your browser to: http://localhost:5000"
        streamlit run app.py --server.port 5000
        ;;
    2)
        echo "Starting LangGraph development server..."
        echo "LangGraph Studio will be available at: http://localhost:8123"
        langgraph dev
        ;;
    3)
        echo "Starting interactive Python console..."
        python -i interactive_workflow.py
        ;;
    *)
        echo "Invalid choice. Starting Streamlit by default..."
        streamlit run app.py --server.port 5000
        ;;
esac

echo "Setup complete! Press Ctrl+C to stop the application."