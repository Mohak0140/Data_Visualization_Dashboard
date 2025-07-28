# Data Visualization API Documentation

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Health Check
**GET** `/`

Returns API status and available endpoints.

**Response:**
```json
{
  "message": "Data Visualization API is running",
  "version": "1.0.0",
  "endpoints": {
    "upload": "/api/upload",
    "data": "/api/data",
    "visualize": "/api/visualize",
    "stats": "/api/stats"
  }
}
```

### 2. Upload CSV File
**POST** `/api/upload`

Upload a CSV file for analysis and visualization.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing CSV file

**Response:**
```json
{
  "dataset_id": "data_csv_0",
  "filename": "data.csv",
  "shape": [100, 5],
  "columns": ["col1", "col2", "col3", "col4", "col5"],
  "dtypes": {
    "col1": "int64",
    "col2": "float64",
    "col3": "object"
  },
  "preview": [
    {"col1": 1, "col2": 2.5, "col3": "value"},
    ...
  ],
  "message": "File uploaded successfully"
}
```

### 3. Get Dataset Data
**GET** `/api/data/{dataset_id}`

Retrieve dataset information and data with pagination.

**Query Parameters:**
- `limit` (optional): Number of rows to return (default: 100)
- `offset` (optional): Number of rows to skip (default: 0)

**Response:**
```json
{
  "dataset_id": "data_csv_0",
  "total_rows": 1000,
  "columns": ["col1", "col2", "col3"],
  "dtypes": {
    "col1": "int64",
    "col2": "float64"
  },
  "data": [
    {"col1": 1, "col2": 2.5},
    ...
  ],
  "pagination": {
    "offset": 0,
    "limit": 100,
    "has_more": true
  }
}
```

### 4. Create Visualization
**POST** `/api/visualize`

Generate a chart based on the provided parameters.

**Request Body:**
```json
{
  "dataset_id": "data_csv_0",
  "chart_type": "scatter",
  "x_axis": "column1",
  "y_axis": "column2",
  "color": "column3",
  "title": "My Chart"
}
```

**Chart Types:**
- `scatter`: Scatter plot (requires x_axis and y_axis)
- `line`: Line chart (requires x_axis and y_axis)
- `bar`: Bar chart (requires x_axis and y_axis)
- `histogram`: Histogram (requires x_axis only)
- `box`: Box plot (requires x_axis, y_axis optional)

**Response:**
```json
{
  "chart_data": {
    "data": [...],
    "layout": {...}
  },
  "chart_type": "scatter",
  "parameters": {
    "x_axis": "column1",
    "y_axis": "column2",
    "color": "column3",
    "title": "My Chart"
  }
}
```

### 5. Get Dataset Statistics
**GET** `/api/stats/{dataset_id}`

Get statistical summary of the dataset.

**Response:**
```json
{
  "dataset_id": "data_csv_0",
  "info": {
    "shape": [1000, 5],
    "columns": ["col1", "col2", "col3"],
    "dtypes": {
      "col1": "int64",
      "col2": "float64"
    },
    "missing_values": {
      "col1": 0,
      "col2": 5
    },
    "memory_usage": {
      "col1": 8000,
      "col2": 8000
    }
  },
  "statistics": {
    "numeric": {
      "col1": {
        "count": 1000,
        "mean": 50.5,
        "std": 28.87,
        "min": 1,
        "25%": 25.75,
        "50%": 50.5,
        "75%": 75.25,
        "max": 100
      }
    },
    "categorical": {
      "col3": {
        "unique_count": 10,
        "top_values": {
          "value1": 100,
          "value2": 95
        }
      }
    }
  }
}
```

### 6. List All Datasets
**GET** `/api/datasets`

Get a list of all uploaded datasets.

**Response:**
```json
{
  "datasets": [
    {
      "dataset_id": "data_csv_0",
      "shape": [1000, 5],
      "columns": ["col1", "col2", "col3"]
    }
  ],
  "count": 1
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `400`: Bad Request - Invalid input or missing required fields
- `404`: Not Found - Dataset or endpoint not found
- `413`: Payload Too Large - File size exceeds 16MB limit
- `500`: Internal Server Error - Server-side error

## File Limitations
- Maximum file size: 16MB
- Supported formats: CSV only
- Files are stored in memory (consider database storage for production)