FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY project_requirements.txt .
RUN pip install --no-cache-dir -r project_requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data indexes

# Expose port for Streamlit
EXPOSE 5000

# Set environment variables
ENV STREAMLIT_SERVER_PORT=5000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]