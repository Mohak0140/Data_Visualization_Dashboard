#!/bin/bash

echo "🚀 Starting Data Visualization Backend API..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source ../venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=True

echo "🌐 Starting Flask server on http://localhost:5000"
echo "📚 API Documentation available in api_docs.md"
echo "🧪 Run 'python test_api.py' to test the API endpoints"
echo ""

# Start the Flask application
python app.py