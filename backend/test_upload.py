#!/usr/bin/env python3
"""
Test script for basic CSV upload functionality
"""

import requests
import json
import os

# Configuration: Change this to switch between different CSV files
CSV_FILES = {
    "balanced": "./trans_data_internal/sample_transactions_balanced.csv",
    "original": "./trans_data_internal/sample_transactions.csv"
}

# Set the default CSV file to use
DEFAULT_CSV = "balanced"  # Change this to "original" to use the other file

def test_upload(csv_type=None):
    """Test the CSV upload endpoint"""
    if csv_type is None:
        csv_type = DEFAULT_CSV
    
    if csv_type not in CSV_FILES:
        print(f"❌ Unknown CSV type: {csv_type}. Available: {list(CSV_FILES.keys())}")
        return None
    
    csv_path = CSV_FILES[csv_type]
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return None
    
    url = "http://localhost:8000/upload-transactions"
    
    print(f"📁 Uploading CSV file: {csv_path}")
    
    # Test with sample file
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path, f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('is_duplicate'):
                    print("🔄 Duplicate detected!")
                    print(f"📁 Existing File ID: {data['file_id']}")
                    print(f"📅 Original upload: {data['original_upload_time']}")
                else:
                    print("✅ Upload successful!")
                    print(f"📁 File ID: {data['file_id']}")
                    print(f"📊 Total rows: {data['rows']}")
                    print(f"📋 Total columns: {data['columns']}")
                return data['file_id']
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
            return None

def test_duplicate_upload(csv_type=None):
    """Test uploading the same file twice to verify duplicate detection"""
    if csv_type is None:
        csv_type = DEFAULT_CSV
    
    if csv_type not in CSV_FILES:
        print(f"❌ Unknown CSV type: {csv_type}. Available: {list(CSV_FILES.keys())}")
        return
    
    csv_path = CSV_FILES[csv_type]
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print("\n🔄 Testing duplicate detection...")
    url = "http://localhost:8000/upload-transactions"
    
    # Upload the same file twice
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path, f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                data = response.json()
                if data.get('is_duplicate'):
                    print("✅ Duplicate detection working correctly!")
                    print(f"📁 Returned existing file ID: {data['file_id']}")
                else:
                    print("⚠️  First upload - this is expected")
            else:
                print(f"❌ Upload failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")

def test_file_list():
    """Test the file listing endpoint"""
    url = "http://localhost:8000/files"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Found {data['total_files']} uploaded files:")
            for file_info in data['files']:
                print(f"  - {file_info['filename']} (ID: {file_info['file_id'][:8]}...)")
        else:
            print(f"❌ Failed to list files: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

def test_hash_registry():
    """Test the hash registry endpoint"""
    url = "http://localhost:8000/files/registry"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Hash Registry: {data['total_hashes']} registered hashes")
        else:
            print(f"❌ Failed to get hash registry: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

if __name__ == "__main__":
    print("🧪 Testing Basic Upload Functionality...")
    print("=" * 50)
    
    # Show available CSV files
    print(f"📁 Available CSV files:")
    for name, path in CSV_FILES.items():
        status = "✅" if os.path.exists(path) else "❌"
        default_marker = " (DEFAULT)" if name == DEFAULT_CSV else ""
        print(f"  {status} {name}: {path}{default_marker}")
    
    print(f"\n🎯 Using CSV file: {DEFAULT_CSV} ({CSV_FILES[DEFAULT_CSV]})")
    print("💡 To change the CSV file, modify the DEFAULT_CSV variable at the top of this file")
    print("=" * 50)
    
    # Test upload
    file_id = test_upload()
    
    # Test duplicate detection
    test_duplicate_upload()
    
    # Test file listing
    test_file_list()
    
    # Test hash registry
    test_hash_registry()
    
    if file_id:
        print(f"\n🔗 You can view the API docs at: http://localhost:8000/docs")
        print(f"📁 File details: http://localhost:8000/files/{file_id}")
        print(f"⬇️  Download file: http://localhost:8000/files/{file_id}/download")
        print(f"🔍 Hash registry: http://localhost:8000/files/registry")