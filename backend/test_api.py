#!/usr/bin/env python3
"""
Test script for the Data Visualization API
"""

import requests
import json
import pandas as pd
import io

# API base URL
BASE_URL = 'http://localhost:5001'

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def create_sample_csv():
    """Create a sample CSV file for testing"""
    print("📄 Creating sample CSV data...")
    
    # Create sample data
    data = {
        'x_values': range(1, 101),
        'y_values': [i * 2 + (i % 10) for i in range(1, 101)],
        'categories': ['A' if i % 3 == 0 else 'B' if i % 3 == 1 else 'C' for i in range(100)],
        'random_values': [i * 0.5 + (i % 7) * 3 for i in range(1, 101)]
    }
    
    df = pd.DataFrame(data)
    csv_string = df.to_csv(index=False)
    return csv_string

def test_upload():
    """Test file upload endpoint"""
    print("📤 Testing file upload...")
    
    csv_data = create_sample_csv()
    
    files = {
        'file': ('test_data.csv', io.StringIO(csv_data), 'text/csv')
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/upload', files=files)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful: {data['message']}")
            print(f"   Dataset ID: {data['dataset_id']}")
            print(f"   Shape: {data['shape']}")
            print(f"   Columns: {data['columns']}")
            return data['dataset_id']
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_get_data(dataset_id):
    """Test get data endpoint"""
    print(f"📊 Testing get data for dataset: {dataset_id}")
    
    try:
        response = requests.get(f'{BASE_URL}/api/data/{dataset_id}?limit=10')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data retrieval successful")
            print(f"   Total rows: {data['total_rows']}")
            print(f"   Returned rows: {len(data['data'])}")
            print(f"   Has more: {data['pagination']['has_more']}")
            return True
        else:
            print(f"❌ Data retrieval failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
        return False

def test_visualization(dataset_id):
    """Test visualization endpoint"""
    print(f"📈 Testing visualization for dataset: {dataset_id}")
    
    # Test scatter plot
    viz_request = {
        'dataset_id': dataset_id,
        'chart_type': 'scatter',
        'x_axis': 'x_values',
        'y_axis': 'y_values',
        'color': 'categories',
        'title': 'Test Scatter Plot'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/visualize',
            json=viz_request,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scatter plot created successfully")
            print(f"   Chart type: {data['chart_type']}")
            print(f"   Parameters: {data['parameters']}")
            
            # Test histogram
            hist_request = {
                'dataset_id': dataset_id,
                'chart_type': 'histogram',
                'x_axis': 'random_values',
                'title': 'Test Histogram'
            }
            
            hist_response = requests.post(
                f'{BASE_URL}/api/visualize',
                json=hist_request,
                headers={'Content-Type': 'application/json'}
            )
            
            if hist_response.status_code == 200:
                print(f"✅ Histogram created successfully")
                return True
            else:
                print(f"❌ Histogram creation failed: {hist_response.status_code}")
                return False
                
        else:
            print(f"❌ Visualization failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return False

def test_statistics(dataset_id):
    """Test statistics endpoint"""
    print(f"📊 Testing statistics for dataset: {dataset_id}")
    
    try:
        response = requests.get(f'{BASE_URL}/api/stats/{dataset_id}')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics generated successfully")
            print(f"   Dataset shape: {data['info']['shape']}")
            print(f"   Numeric columns: {len(data['statistics'].get('numeric', {}))}")
            print(f"   Categorical columns: {len(data['statistics'].get('categorical', {}))}")
            return True
        else:
            print(f"❌ Statistics failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return False

def test_list_datasets():
    """Test list datasets endpoint"""
    print("📋 Testing list datasets...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/datasets')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset list retrieved successfully")
            print(f"   Total datasets: {data['count']}")
            return True
        else:
            print(f"❌ List datasets failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ List datasets error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Starting API Tests")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("💥 Health check failed. Make sure the API is running.")
        return
    
    print()
    
    # Test upload
    dataset_id = test_upload()
    if not dataset_id:
        print("💥 Upload test failed. Cannot continue with other tests.")
        return
    
    print()
    
    # Test other endpoints
    tests = [
        ('Get Data', lambda: test_get_data(dataset_id)),
        ('Visualization', lambda: test_visualization(dataset_id)),
        ('Statistics', lambda: test_statistics(dataset_id)),
        ('List Datasets', test_list_datasets)
    ]
    
    passed = 2  # Already passed health check and upload
    total = len(tests) + 2  # +2 for health check and upload
    
    for test_name, test_func in tests:
        print()
        if test_func():
            passed += 1
    
    print()
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == '__main__':
    main()