#!/usr/bin/env python3
"""
Test script for basic CSV upload functionality
"""

import requests
import json

def test_upload():
    """Test the CSV upload endpoint"""
    url = "http://localhost:8000/upload-transactions"
    
    # Test with sample file
    with open("./trans_data_internal/sample_transactions.csv", "rb") as f:
        files = {"file": ("./trans_data_internal/sample_transactions.csv", f, "text/csv")}
        
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

def test_duplicate_upload():
    """Test uploading the same file twice to verify duplicate detection"""
    print("\n🔄 Testing duplicate detection...")
    url = "http://localhost:8000/upload-transactions"
    
    # Upload the same file twice
    with open("./trans_data_internal/sample_transactions.csv", "rb") as f:
        files = {"file": ("./trans_data_internal/sample_transactions.csv", f, "text/csv")}
        
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