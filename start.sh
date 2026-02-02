#!/bin/bash
# Startup script for Document Types Dependency Visualization

echo "Starting Document Types Dependency Visualization..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start Flask application
echo "Starting Flask server..."
cd backend
python app.py
