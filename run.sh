#!/bin/bash

# Data Visualization Dashboard Runner
echo "🚀 Starting Data Visualization Dashboard..."

# Activate virtual environment
source venv/bin/activate

# Run the Streamlit application
echo "📊 Launching Streamlit application..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

echo "✅ Application should be available at http://localhost:8501"