# 📊 Data Visualization Dashboard

A comprehensive web application for CSV data analysis and visualization with both integrated Streamlit interface and separate Flask REST API backend.

## 🏗️ Architecture

This project provides **two different approaches** for building data visualization applications:

### 1. **Streamlit Application** (Integrated Frontend + Backend)
- **File**: `app.py`
- **Technology**: Streamlit framework
- **Port**: `8501`
- **Features**: All-in-one solution with built-in UI and data processing

### 2. **Flask REST API Backend** + **HTML Frontend**
- **Backend**: `backend/app.py` (Flask API)
- **Frontend**: `frontend.html` (HTML/JavaScript)
- **Port**: Backend on `5001`, Frontend via file system
- **Features**: Decoupled architecture, RESTful API, custom frontend

## 🚀 Quick Start

### Option 1: Run Streamlit Application
```bash
# Start the integrated Streamlit app
./run.sh
# Access at: http://localhost:8501
```

### Option 2: Run Flask Backend + HTML Frontend
```bash
# Start Flask API server
cd backend && ./run_backend.sh
# Access API at: http://localhost:5001
# Open frontend.html in your browser
```

## 📁 Project Structure

```
Data_Visualization_Dashboard/
├── 📱 STREAMLIT APPLICATION
│   ├── app.py                 # Main Streamlit app
│   ├── requirements.txt       # Streamlit dependencies
│   └── run.sh                # Streamlit startup script
│
├── 🔧 FLASK BACKEND
│   ├── backend/
│   │   ├── app.py            # Flask REST API
│   │   ├── config.py         # Configuration management
│   │   ├── .env              # Environment variables
│   │   ├── requirements.txt  # Flask dependencies
│   │   ├── run_backend.sh    # Backend startup script
│   │   ├── test_api.py       # API test suite
│   │   └── api_docs.md       # API documentation
│   │
├── 🎨 FRONTEND
│   └── frontend.html         # HTML/JS frontend
│
├── 🔧 SHARED
│   ├── venv/                 # Python virtual environment
│   └── README.md            # This file
```

## ✨ Features

### 📊 Data Processing
- **CSV File Upload**: Support for CSV files up to 16MB
- **Data Preview**: Interactive table display of uploaded data
- **Data Validation**: Automatic data type detection and validation
- **Statistical Analysis**: Comprehensive descriptive statistics

### 📈 Visualizations
- **Scatter Plots**: Explore relationships between variables
- **Line Charts**: Track trends over time or sequences
- **Bar Charts**: Compare categorical data
- **Histograms**: Analyze data distributions
- **Box Plots**: Visualize data quartiles and outliers

### 🎛️ Interactive Controls
- **Dynamic Column Selection**: Choose X-axis, Y-axis, and color mapping
- **Chart Type Switching**: Change visualization types on the fly
- **Real-time Updates**: Instant chart generation and updates
- **Data Pagination**: Handle large datasets efficiently

## 🛠️ Technical Stack

### Backend Technologies
- **Python 3.13+**
- **Flask 3.0.0** - Web framework for REST API
- **Streamlit 1.47.1** - Interactive web app framework
- **Pandas 2.3.1** - Data manipulation and analysis
- **Plotly 6.2.0** - Interactive visualization library
- **NumPy 2.3.2** - Numerical computing

### Frontend Technologies
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive functionality
- **Plotly.js** - Client-side charting library
- **Fetch API** - HTTP requests to backend

## 📚 API Documentation

### Base URL
```
http://localhost:5001
```

### Key Endpoints

#### Upload CSV File
```http
POST /api/upload
Content-Type: multipart/form-data

Response: Dataset information and preview
```

#### Create Visualization
```http
POST /api/visualize
Content-Type: application/json

{
  "dataset_id": "string",
  "chart_type": "scatter|line|bar|histogram|box",
  "x_axis": "column_name",
  "y_axis": "column_name",
  "color": "column_name"
}
```

#### Get Statistics
```http
GET /api/stats/{dataset_id}

Response: Comprehensive dataset statistics
```

**Full API documentation**: `backend/api_docs.md`

## 🧪 Testing

### Test Flask API
```bash
cd backend
python test_api.py
```

### Test Streamlit App
```bash
# Start the app and test via web interface
./run.sh
```

## 🔧 Development Setup

### Prerequisites
- Python 3.13+
- pip package manager
- Web browser (for frontend)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Data_Visualization_Dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

## 🌐 Usage Examples

### Using Streamlit Interface
1. Run `./run.sh`
2. Open http://localhost:8501
3. Upload CSV file using the file uploader
4. Configure chart parameters in sidebar
5. View interactive visualizations

### Using Flask API + HTML Frontend
1. Start backend: `cd backend && ./run_backend.sh`
2. Open `frontend.html` in your browser
3. Upload CSV file via the web interface
4. Create visualizations using the controls
5. View statistics and data insights

## 🔒 Security Considerations

- **File Size Limits**: 16MB maximum upload size
- **File Type Validation**: Only CSV files accepted
- **CORS Enabled**: Cross-origin requests allowed for development
- **Input Validation**: All API inputs validated and sanitized

## 🚀 Deployment

### Development
Both applications are configured for development with debug mode enabled.

### Production
- **Streamlit**: Use `streamlit run app.py --server.port 8501 --server.address 0.0.0.0`
- **Flask**: Use a WSGI server like Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5001 backend.app:app`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

- **API Issues**: Check `backend/api_docs.md`
- **Testing**: Run `backend/test_api.py`
- **Logs**: Check `backend/flask.log` for Flask issues