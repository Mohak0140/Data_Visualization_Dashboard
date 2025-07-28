from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import io
import os
import sys
import subprocess
from pathlib import Path
from werkzeug.utils import secure_filename
import numpy as np

def setup_environment():
    """Setup environment and install dependencies if needed"""
    print("🔍 Checking environment setup...")
    
    # Check if virtual environment exists
    venv_path = Path("../venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Creating it...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "../venv"], check=True)
            print("✅ Virtual environment created successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            sys.exit(1)
    
    # Check if we're in the virtual environment
    in_venv = (hasattr(sys, 'real_prefix') or 
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    
    if not in_venv:
        print("⚠️  Not running in virtual environment")
        print("💡 Tip: Activate with 'source ../venv/bin/activate'")
    
    # Check and install dependencies
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print("📦 Checking dependencies...")
        try:
            # Try importing required packages
            import flask
            import flask_cors
            import pandas
            import plotly
            import numpy
            print("✅ All dependencies are installed")
        except ImportError as e:
            print(f"📦 Installing missing dependency: {e}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
                print("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                print("💡 Try: pip install -r requirements.txt")
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print(f"📁 Uploads directory: {uploads_dir.absolute()}")

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    return app

# Initialize Flask app
app = create_app()
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Store uploaded data in memory (in production, use a database)
uploaded_data = {}

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint with system information"""
    return jsonify({
        'message': 'Data Visualization API is running',
        'version': '1.0.0',
        'python_version': sys.version.split()[0],
        'working_directory': os.getcwd(),
        'uploaded_datasets': len(uploaded_data),
        'endpoints': {
            'upload': '/api/upload',
            'data': '/api/data',
            'visualize': '/api/visualize',
            'stats': '/api/stats',
            'datasets': '/api/datasets'
        },
        'status': {
            'flask': '✅ Running',
            'cors': '✅ Enabled',
            'uploads': '✅ Ready'
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400
        
        # Read CSV data
        csv_data = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))
        
        # Generate a unique ID for this dataset
        dataset_id = secure_filename(file.filename) + '_' + str(len(uploaded_data))
        
        # Store the dataframe
        uploaded_data[dataset_id] = df
        
        print(f"📤 File uploaded: {file.filename} -> {dataset_id} (Shape: {df.shape})")
        
        # Return dataset info
        return jsonify({
            'dataset_id': dataset_id,
            'filename': file.filename,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'preview': df.head().to_dict('records'),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
            'missing_values': df.isnull().sum().sum(),
            'message': 'File uploaded successfully'
        })
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/data/<dataset_id>', methods=['GET'])
def get_data(dataset_id):
    """Get dataset information and preview"""
    try:
        if dataset_id not in uploaded_data:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = uploaded_data[dataset_id]
        
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Apply pagination
        paginated_df = df.iloc[offset:offset+limit]
        
        return jsonify({
            'dataset_id': dataset_id,
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'data': paginated_df.to_dict('records'),
            'pagination': {
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < len(df)
            },
            'summary': {
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
                'missing_values': df.isnull().sum().sum(),
                'numeric_columns': len(df.select_dtypes(include=['number']).columns),
                'categorical_columns': len(df.select_dtypes(include=['object']).columns)
            }
        })
    
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
        return jsonify({'error': f'Error retrieving data: {str(e)}'}), 500

@app.route('/api/visualize', methods=['POST'])
def create_visualization():
    """Create visualization based on parameters"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        dataset_id = data.get('dataset_id')
        chart_type = data.get('chart_type', 'scatter')
        x_axis = data.get('x_axis')
        y_axis = data.get('y_axis')
        color = data.get('color')
        title = data.get('title', f'{chart_type.title()} Chart')
        
        if dataset_id not in uploaded_data:
            return jsonify({'error': 'Dataset not found'}), 404
        
        if not x_axis:
            return jsonify({'error': 'X-axis column is required'}), 400
        
        df = uploaded_data[dataset_id]
        
        # Validate columns exist
        if x_axis not in df.columns:
            return jsonify({'error': f'Column {x_axis} not found in dataset'}), 400
        
        if y_axis and y_axis not in df.columns:
            return jsonify({'error': f'Column {y_axis} not found in dataset'}), 400
        
        if color and color not in df.columns:
            return jsonify({'error': f'Column {color} not found in dataset'}), 400
        
        # Create visualization based on chart type
        fig = None
        
        if chart_type == 'scatter':
            if not y_axis:
                return jsonify({'error': 'Y-axis is required for scatter plot'}), 400
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color, title=title)
        
        elif chart_type == 'line':
            if not y_axis:
                return jsonify({'error': 'Y-axis is required for line plot'}), 400
            fig = px.line(df, x=x_axis, y=y_axis, color=color, title=title)
        
        elif chart_type == 'bar':
            if not y_axis:
                return jsonify({'error': 'Y-axis is required for bar plot'}), 400
            fig = px.bar(df, x=x_axis, y=y_axis, color=color, title=title)
        
        elif chart_type == 'histogram':
            fig = px.histogram(df, x=x_axis, color=color, title=title)
        
        elif chart_type == 'box':
            if y_axis:
                fig = px.box(df, x=x_axis, y=y_axis, color=color, title=title)
            else:
                fig = px.box(df, y=x_axis, color=color, title=title)
        
        else:
            return jsonify({'error': f'Unsupported chart type: {chart_type}'}), 400
        
        if fig is None:
            return jsonify({'error': 'Failed to create visualization'}), 500
        
        # Convert to JSON
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        print(f"📊 Visualization created: {chart_type} chart for {dataset_id}")
        
        return jsonify({
            'chart_data': json.loads(graph_json),
            'chart_type': chart_type,
            'parameters': {
                'x_axis': x_axis,
                'y_axis': y_axis,
                'color': color,
                'title': title
            },
            'dataset_info': {
                'rows_used': len(df),
                'columns_used': [col for col in [x_axis, y_axis, color] if col]
            }
        })
    
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return jsonify({'error': f'Error creating visualization: {str(e)}'}), 500

@app.route('/api/stats/<dataset_id>', methods=['GET'])
def get_statistics(dataset_id):
    """Get statistical summary of the dataset"""
    try:
        if dataset_id not in uploaded_data:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = uploaded_data[dataset_id]
        
        # Get basic info
        info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).to_dict()
        }
        
        # Get descriptive statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        stats = {}
        
        if numeric_columns:
            stats['numeric'] = df[numeric_columns].describe().to_dict()
        
        if categorical_columns:
            categorical_stats = {}
            for col in categorical_columns:
                categorical_stats[col] = {
                    'unique_count': df[col].nunique(),
                    'top_values': df[col].value_counts().head(10).to_dict(),
                    'missing_count': df[col].isnull().sum()
                }
            stats['categorical'] = categorical_stats
        
        print(f"📈 Statistics generated for {dataset_id}")
        
        return jsonify({
            'dataset_id': dataset_id,
            'info': info,
            'statistics': stats,
            'summary': {
                'total_missing': df.isnull().sum().sum(),
                'numeric_columns': len(numeric_columns),
                'categorical_columns': len(categorical_columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
            }
        })
    
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return jsonify({'error': f'Error generating statistics: {str(e)}'}), 500

@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """List all uploaded datasets"""
    datasets = []
    for dataset_id, df in uploaded_data.items():
        datasets.append({
            'dataset_id': dataset_id,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
            'missing_values': df.isnull().sum().sum()
        })
    
    return jsonify({
        'datasets': datasets,
        'count': len(datasets),
        'total_memory': sum(df.memory_usage(deep=True).sum() for df in uploaded_data.values()) / 1024
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

def start_server():
    """Start the Flask development server"""
    print("🚀 Starting Data Visualization Backend API...")
    print("=" * 50)
    print(f"🌐 Server will run on: http://localhost:5001")
    print(f"📚 API Documentation: backend/api_docs.md")
    print(f"🧪 Test API: python test_api.py")
    print(f"🎨 Frontend: Open frontend.html in browser")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    # Setup environment and dependencies
    setup_environment()
    
    # Start the server
    start_server()